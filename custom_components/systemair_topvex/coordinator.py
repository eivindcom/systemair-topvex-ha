"""DataUpdateCoordinator for Systemair Topvex."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ALARM_NAMES,
    ALARM_STATUSES,
    AHU_MODES,
    BOOST_EAF_FLOW,
    BOOST_SAF_FLOW,
    DOMAIN,
    FAN_MODES,
    FAN_TYPES,
    HR,
    IR,
    UNIT_MODES,
    VENT_CONTROL_TYPES,
)
from .modbus_client import TopvexModbusClient, signed16

_LOGGER = logging.getLogger(__name__)


@dataclass
class AlarmInfo:
    """Single alarm entry."""
    id: int
    name: str
    status: int
    status_name: str


@dataclass
class TopvexData:
    """All data from the Topvex unit."""
    # Temperatures
    outdoor_temp: float | None = None
    intake_temp: float | None = None
    supply_temp: float | None = None
    exhaust_temp: float | None = None
    extract_temp: float | None = None
    after_recovery_temp: float | None = None

    # Flow (m³/h)
    saf_flow: float | None = None
    eaf_flow: float | None = None

    # Fan output (%)
    saf_output: float | None = None
    eaf_output: float | None = None

    # Pressure (Pa)
    exch_pressure: float | None = None
    filter_pressure_saf: float | None = None
    filter_pressure_eaf: float | None = None

    # Special sensors
    recovery_efficiency: float | None = None
    frost_protection: float | None = None
    seq_b: float | None = None  # bypass

    # Environment
    co2: float | None = None
    humidity_room: float | None = None
    humidity_duct: float | None = None
    humidity_outdoor: float | None = None

    # Unit mode
    unit_mode: int | None = None
    unit_mode_name: str | None = None

    # Settings
    ahu_mode: int | None = None
    ahu_mode_name: str | None = None
    manual_submode: int | None = None
    saf_mode: int | None = None
    saf_mode_name: str | None = None
    saf_manual_setpoint: float | None = None
    saf_manual_output: float | None = None
    eaf_mode: int | None = None
    eaf_mode_name: str | None = None
    eaf_manual_setpoint: float | None = None
    eaf_manual_output: float | None = None

    # Temperature setpoints
    vent_control: int | None = None
    vent_control_name: str | None = None
    fan_type: int | None = None
    fan_type_name: str | None = None
    supply_setpoint: float | None = None
    extract_setpoint: float | None = None
    supply_setpoint_max: float | None = None
    supply_setpoint_min: float | None = None

    # Fan flow setpoints (m³/h)
    saf_flow_low: float | None = None
    saf_flow_normal: float | None = None
    saf_flow_high: float | None = None
    eaf_flow_low: float | None = None
    eaf_flow_normal: float | None = None
    eaf_flow_high: float | None = None

    # Bypass
    bypass_mode: int | None = None
    bypass_manual_output: float | None = None

    # Alarms
    alarms: list[AlarmInfo] = field(default_factory=list)

    # Kitchen boost
    boost_active: bool = False
    boost_remaining: int = 0


class TopvexCoordinator(DataUpdateCoordinator[TopvexData]):
    """Coordinator for polling the Topvex unit."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: TopvexModbusClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self._poll_cycle = 0

        # Kitchen boost state
        self._boost_active = False
        self._boost_ends_at: float = 0
        self._boost_cancel: callback | None = None
        self._boost_saved: dict | None = None

    async def _async_update_data(self) -> TopvexData:
        """Fetch data from Topvex via Modbus."""
        if not self.client.connected:
            try:
                connected = await self.client.connect()
                if not connected:
                    raise UpdateFailed("Cannot connect to Topvex")
            except Exception as err:
                raise UpdateFailed(f"Connection error: {err}") from err

        data = TopvexData()
        try:
            await self._read_sensors(data)
            await self._read_settings(data)

            # Alarms every 6th cycle (~60s at 10s interval)
            if self._poll_cycle % 6 == 0:
                await self._read_alarms(data)
            elif self.data:
                data.alarms = self.data.alarms

            self._poll_cycle += 1

            # Boost state
            if self._boost_active:
                import time
                remaining = max(0, int(self._boost_ends_at - time.time()))
                data.boost_active = True
                data.boost_remaining = remaining
                if remaining == 0:
                    self._boost_active = False

        except Exception as err:
            raise UpdateFailed(f"Polling error: {err}") from err

        return data

    async def _read_sensors(self, data: TopvexData) -> None:
        """Read all sensor input registers."""
        # Batch 1: IR 290-304 (15 regs) — temps, flow, pressure
        ir1 = await self.client.read_input_registers(290, 15)
        if ir1:
            raw_outdoor = signed16(ir1[0]) / 10
            data.intake_temp = signed16(ir1[1]) / 10
            data.supply_temp = signed16(ir1[2]) / 10
            data.exhaust_temp = signed16(ir1[3]) / 10
            data.extract_temp = signed16(ir1[4]) / 10
            # Fallback: use intake if outdoor sensor reads 0
            data.outdoor_temp = data.intake_temp if raw_outdoor == 0 else raw_outdoor
            data.saf_flow = ir1[11] / 10  # IR 301, raw is 10x
            data.eaf_flow = ir1[12] / 10  # IR 302, raw is 10x
            data.exch_pressure = signed16(ir1[14]) / 10  # IR 304

        # Individual: IR 323-325 (may fail in batch)
        data.filter_pressure_saf = await self.client.read_input_register_single(IR.FILTER_PRESSURE_SAF)
        data.filter_pressure_eaf = await self.client.read_input_register_single(IR.FILTER_PRESSURE_EAF)
        data.after_recovery_temp = await self.client.read_input_register_single(IR.AFTER_RECOVERY_TEMP)

        # Individual: IR 341-342 (SEQ-A/B)
        ir_seq = await self.client.read_input_registers(341, 2)
        if ir_seq:
            data.seq_b = signed16(ir_seq[1]) / 10  # SEQ-B = bypass

        # Batch: IR 353-354 (fan outputs)
        ir2 = await self.client.read_input_registers(353, 2)
        if ir2:
            data.saf_output = signed16(ir2[0]) / 10
            data.eaf_output = signed16(ir2[1]) / 10

        # Individual: IR 374 (frost protection)
        data.frost_protection = await self.client.read_input_register_single(IR.FROST_PROTECTION)

        # Individual: IR 395-396 (efficiency + unit mode)
        ir3 = await self.client.read_input_registers(395, 2)
        if ir3:
            data.recovery_efficiency = signed16(ir3[0]) / 10
            data.unit_mode = ir3[1]
            data.unit_mode_name = UNIT_MODES.get(ir3[1], f"Ukjent ({ir3[1]})")
        else:
            # Fallback: just unit mode
            ir3f = await self.client.read_input_registers(396, 1)
            if ir3f:
                data.unit_mode = ir3f[0]
                data.unit_mode_name = UNIT_MODES.get(ir3f[0], f"Ukjent ({ir3f[0]})")

        # Batch: IR 309-312 (CO2, humidity)
        ir4 = await self.client.read_input_registers(309, 4)
        if ir4:
            data.co2 = signed16(ir4[0]) / 10
            data.humidity_room = signed16(ir4[1]) / 10
            data.humidity_duct = signed16(ir4[2]) / 10
            data.humidity_outdoor = signed16(ir4[3]) / 10

    async def _read_settings(self, data: TopvexData) -> None:
        """Read holding registers for settings."""
        # HR 565-574 (10 regs: mode settings)
        hr1 = await self.client.read_holding_registers(565, 10)
        if hr1:
            data.ahu_mode = signed16(hr1[0])
            data.ahu_mode_name = AHU_MODES.get(data.ahu_mode, "?")
            data.manual_submode = signed16(hr1[1])
            data.saf_mode = signed16(hr1[2])
            data.saf_mode_name = FAN_MODES.get(data.saf_mode, "?")
            data.saf_manual_setpoint = signed16(hr1[3]) / 10
            data.saf_manual_output = signed16(hr1[4]) / 10
            data.eaf_mode = signed16(hr1[5])
            data.eaf_mode_name = FAN_MODES.get(data.eaf_mode, "?")
            data.eaf_manual_setpoint = signed16(hr1[6]) / 10
            data.eaf_manual_output = signed16(hr1[7]) / 10

        # HR 585-593 (9 regs: temp settings)
        hr2 = await self.client.read_holding_registers(585, 9)
        if hr2:
            data.vent_control = signed16(hr2[0])
            data.vent_control_name = VENT_CONTROL_TYPES.get(data.vent_control, "?")
            data.fan_type = signed16(hr2[1])
            data.fan_type_name = FAN_TYPES.get(data.fan_type, "?")
            data.supply_setpoint = signed16(hr2[3]) / 10
            data.extract_setpoint = signed16(hr2[4]) / 10
            data.supply_setpoint_max = signed16(hr2[5]) / 10
            data.supply_setpoint_min = signed16(hr2[6]) / 10

        # HR 618-629 (12 regs: fan setpoints)
        hr3 = await self.client.read_holding_registers(618, 12)
        if hr3:
            data.saf_flow_low = signed16(hr3[0]) / 10
            data.saf_flow_normal = signed16(hr3[1]) / 10
            data.saf_flow_high = signed16(hr3[2]) / 10
            data.eaf_flow_low = signed16(hr3[3]) / 10
            data.eaf_flow_normal = signed16(hr3[4]) / 10
            data.eaf_flow_high = signed16(hr3[5]) / 10

        # HR 719-720 (bypass control)
        hr4 = await self.client.read_holding_registers(719, 2)
        if hr4:
            data.bypass_mode = signed16(hr4[0])
            data.bypass_manual_output = signed16(hr4[1]) / 10

    async def _read_alarms(self, data: TopvexData) -> None:
        """Read alarm registers IR 0-159."""
        alarms = []
        all_regs: list[int] = []

        for start in (0, 47, 94, 141):
            count = min(47, 160 - start)
            regs = await self.client.read_input_registers(start, count)
            if regs:
                all_regs.extend(regs)
            else:
                all_regs.extend([1] * count)  # Assume OK on read failure

        for i, status in enumerate(all_regs):
            if status not in (0, 1):
                alarms.append(AlarmInfo(
                    id=i,
                    name=ALARM_NAMES.get(i, f"Alarm {i}"),
                    status=status,
                    status_name=ALARM_STATUSES.get(status, f"Ukjent ({status})"),
                ))

        data.alarms = alarms

    # --- Write commands ---

    async def async_set_ahu_mode(self, mode: int) -> None:
        """Set AHU operating mode. Auto-sets fans to Auto for modes 2-5."""
        await self.client.write_register(HR.AHU_MODE, mode)
        if mode >= 2:
            await self.client.write_register(HR.SAF_MODE, 2)
            await self.client.write_register(HR.EAF_MODE, 2)
        await self.async_request_refresh()

    async def async_set_manual_submode(self, submode: int) -> None:
        """Set manual submode."""
        await self.client.write_register(HR.MANUAL_SUBMODE, submode)
        await self.async_request_refresh()

    async def async_set_supply_setpoint(self, temp: float) -> None:
        """Set supply air temperature setpoint (°C)."""
        await self.client.write_register(HR.SUPPLY_SETPOINT, round(temp * 10))
        await self.async_request_refresh()

    async def async_set_saf_mode(self, mode: int) -> None:
        """Set supply air fan mode."""
        await self.client.write_register(HR.SAF_MODE, mode)
        await self.async_request_refresh()

    async def async_set_eaf_mode(self, mode: int) -> None:
        """Set extract air fan mode."""
        await self.client.write_register(HR.EAF_MODE, mode)
        await self.async_request_refresh()

    async def async_set_saf_manual_output(self, pct: float) -> None:
        """Set SAF manual output % (min 25). Auto-sets AHU=Manual, SAF=Man.utgang."""
        pct = max(25, min(100, pct))
        # Ensure AHU is in Manual mode and SAF fan mode is "Manuell utgang" (1)
        if not self.data or self.data.ahu_mode != 1:
            await self.client.write_register(HR.AHU_MODE, 1)
        if not self.data or self.data.saf_mode != 1:
            await self.client.write_register(HR.SAF_MODE, 1)
        await self.client.write_register(HR.SAF_MANUAL_OUTPUT, round(pct * 10))
        await self.async_request_refresh()

    async def async_set_eaf_manual_output(self, pct: float) -> None:
        """Set EAF manual output % (min 25). Auto-sets AHU=Manual, EAF=Man.utgang."""
        pct = max(25, min(100, pct))
        # Ensure AHU is in Manual mode and EAF fan mode is "Manuell utgang" (1)
        if not self.data or self.data.ahu_mode != 1:
            await self.client.write_register(HR.AHU_MODE, 1)
        if not self.data or self.data.eaf_mode != 1:
            await self.client.write_register(HR.EAF_MODE, 1)
        await self.client.write_register(HR.EAF_MANUAL_OUTPUT, round(pct * 10))
        await self.async_request_refresh()

    async def async_set_saf_manual_setpoint(self, flow: float) -> None:
        """Set SAF manual flow setpoint (m³/h). Auto-sets AHU=Manual, SAF=Man.SP."""
        flow = max(100, min(2000, flow))
        # Ensure AHU is in Manual mode and SAF fan mode is "Manuelt settpunkt" (3)
        if not self.data or self.data.ahu_mode != 1:
            await self.client.write_register(HR.AHU_MODE, 1)
        if not self.data or self.data.saf_mode != 3:
            await self.client.write_register(HR.SAF_MODE, 3)
        await self.client.write_register(HR.SAF_MANUAL_SETPOINT, round(flow * 10))
        await self.async_request_refresh()

    async def async_set_eaf_manual_setpoint(self, flow: float) -> None:
        """Set EAF manual flow setpoint (m³/h). Auto-sets AHU=Manual, EAF=Man.SP."""
        flow = max(100, min(2000, flow))
        # Ensure AHU is in Manual mode and EAF fan mode is "Manuelt settpunkt" (3)
        if not self.data or self.data.ahu_mode != 1:
            await self.client.write_register(HR.AHU_MODE, 1)
        if not self.data or self.data.eaf_mode != 3:
            await self.client.write_register(HR.EAF_MODE, 3)
        await self.client.write_register(HR.EAF_MANUAL_SETPOINT, round(flow * 10))
        await self.async_request_refresh()

    async def async_set_bypass_mode(self, mode: int) -> None:
        """Set bypass mode (0=Auto, 1=Manual)."""
        await self.client.write_register(HR.BYPASS_MODE, mode)
        await self.async_request_refresh()

    async def async_set_bypass_output(self, pct: float) -> None:
        """Set bypass manual output %."""
        pct = max(0, min(100, pct))
        await self.client.write_register(HR.BYPASS_OUTPUT, round(pct * 10))
        await self.async_request_refresh()

    async def async_acknowledge_alarms(self) -> None:
        """Acknowledge all alarms."""
        await self.client.write_coil(0, True)
        await self.async_request_refresh()

    async def async_reset_filter_alarm(self) -> None:
        """Reset filter alarm counter."""
        await self.client.write_coil(1, True)
        await self.async_request_refresh()

    # --- Kitchen boost ---

    async def async_start_kitchen_boost(self, minutes: int) -> None:
        """Start kitchen boost mode."""
        import time

        if self._boost_active and self._boost_cancel:
            self._boost_cancel()
            self._boost_cancel = None
        elif not self._boost_active and self.data:
            self._boost_saved = {
                "saf_mode": self.data.saf_mode,
                "eaf_mode": self.data.eaf_mode,
                "saf_manual_setpoint": self.data.saf_manual_setpoint,
                "eaf_manual_setpoint": self.data.eaf_manual_setpoint,
            }

        await self.client.write_register(HR.SAF_MODE, 3)
        await self.client.write_register(HR.EAF_MODE, 3)
        await self.client.write_register(
            HR.SAF_MANUAL_SETPOINT, round(BOOST_SAF_FLOW * 10)
        )
        await self.client.write_register(
            HR.EAF_MANUAL_SETPOINT, round(BOOST_EAF_FLOW * 10)
        )

        self._boost_active = True
        self._boost_ends_at = time.time() + minutes * 60

        self._boost_cancel = async_call_later(
            self.hass, minutes * 60, self._async_boost_expired
        )

        _LOGGER.info("Kitchen boost started: %d minutes", minutes)
        await self.async_request_refresh()

    async def _async_boost_expired(self, _now=None) -> None:
        """Restore settings after kitchen boost."""
        await self._async_restore_from_boost()

    async def async_cancel_kitchen_boost(self) -> None:
        """Cancel kitchen boost and restore settings."""
        if self._boost_cancel:
            self._boost_cancel()
            self._boost_cancel = None
        await self._async_restore_from_boost()

    async def _async_restore_from_boost(self) -> None:
        """Restore saved fan settings."""
        if self._boost_saved:
            saved = self._boost_saved
            try:
                await self.client.write_register(HR.SAF_MODE, saved["saf_mode"])
                await self.client.write_register(HR.EAF_MODE, saved["eaf_mode"])
                if saved["saf_mode"] == 3 and saved["saf_manual_setpoint"] is not None:
                    await self.client.write_register(
                        HR.SAF_MANUAL_SETPOINT,
                        round(saved["saf_manual_setpoint"] * 10),
                    )
                if saved["eaf_mode"] == 3 and saved["eaf_manual_setpoint"] is not None:
                    await self.client.write_register(
                        HR.EAF_MANUAL_SETPOINT,
                        round(saved["eaf_manual_setpoint"] * 10),
                    )
            except Exception:
                _LOGGER.exception("Error restoring from kitchen boost")

        self._boost_active = False
        self._boost_ends_at = 0
        self._boost_saved = None
        self._boost_cancel = None
        _LOGGER.info("Kitchen boost ended, settings restored")
        await self.async_request_refresh()
