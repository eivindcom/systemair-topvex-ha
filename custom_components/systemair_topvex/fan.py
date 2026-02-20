"""Fan entities for Systemair Topvex (SAF and EAF)."""
from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN_MODES
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex fans."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TopvexFan(coordinator, "saf", "Tilluftvifte"),
        TopvexFan(coordinator, "eaf", "Avtrekksvifte"),
    ])


class TopvexFan(TopvexEntity, FanEntity):
    """Supply or extract air fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    )
    _attr_speed_count = 100
    _attr_preset_modes = list(FAN_MODES.values())

    def __init__(
        self, coordinator: TopvexCoordinator, fan_id: str, name: str
    ) -> None:
        super().__init__(coordinator, f"fan_{fan_id}", name)
        self._fan_id = fan_id
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool | None:
        """Return True if fan is on."""
        if self.coordinator.data is None:
            return None
        output = self._get_output()
        return output is not None and output > 0

    @property
    def percentage(self) -> int | None:
        """Return fan speed percentage."""
        output = self._get_output()
        if output is None:
            return None
        return int(round(output))

    @property
    def preset_mode(self) -> str | None:
        """Return current fan mode."""
        if self.coordinator.data is None:
            return None
        mode = self._get_mode()
        return FAN_MODES.get(mode)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        if self.coordinator.data is None:
            return {}
        d = self.coordinator.data
        if self._fan_id == "saf":
            return {
                "flow": d.saf_flow,
                "mode_raw": d.saf_mode,
                "manual_setpoint": d.saf_manual_setpoint,
                "manual_output": d.saf_manual_output,
            }
        return {
            "flow": d.eaf_flow,
            "mode_raw": d.eaf_mode,
            "manual_setpoint": d.eaf_manual_setpoint,
            "manual_output": d.eaf_manual_output,
        }

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed percentage (min 25%)."""
        pct = max(25, min(100, percentage))
        if self._fan_id == "saf":
            await self.coordinator.async_set_saf_mode(1)  # Manual output
            await self.coordinator.async_set_saf_manual_output(pct)
        else:
            await self.coordinator.async_set_eaf_mode(1)
            await self.coordinator.async_set_eaf_manual_output(pct)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set fan preset mode."""
        mode_val = None
        for k, v in FAN_MODES.items():
            if v == preset_mode:
                mode_val = k
                break
        if mode_val is None:
            return
        if self._fan_id == "saf":
            await self.coordinator.async_set_saf_mode(mode_val)
        else:
            await self.coordinator.async_set_eaf_mode(mode_val)

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None:
        """Turn fan on."""
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        elif percentage:
            await self.async_set_percentage(percentage)
        else:
            # Default to Auto
            if self._fan_id == "saf":
                await self.coordinator.async_set_saf_mode(2)
            else:
                await self.coordinator.async_set_eaf_mode(2)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn fan off."""
        if self._fan_id == "saf":
            await self.coordinator.async_set_saf_mode(0)
        else:
            await self.coordinator.async_set_eaf_mode(0)

    def _get_output(self) -> float | None:
        if self.coordinator.data is None:
            return None
        if self._fan_id == "saf":
            return self.coordinator.data.saf_output
        return self.coordinator.data.eaf_output

    def _get_mode(self) -> int | None:
        if self.coordinator.data is None:
            return None
        if self._fan_id == "saf":
            return self.coordinator.data.saf_mode
        return self.coordinator.data.eaf_mode
