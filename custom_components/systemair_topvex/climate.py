"""Climate entity for Systemair Topvex."""
from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity

PRESET_AUTO = "auto"
PRESET_LOW = "lav"
PRESET_NORMAL = "normal"
PRESET_HIGH = "høy"

PRESET_TO_AHU_MODE = {
    PRESET_AUTO: 2,
    PRESET_LOW: 3,
    PRESET_NORMAL: 4,
    PRESET_HIGH: 5,
}

AHU_MODE_TO_PRESET = {v: k for k, v in PRESET_TO_AHU_MODE.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex climate."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TopvexClimate(coordinator)])


class TopvexClimate(TopvexEntity, ClimateEntity):
    """Main ventilation climate control."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY]
    _attr_preset_modes = [PRESET_AUTO, PRESET_LOW, PRESET_NORMAL, PRESET_HIGH]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 10
    _attr_max_temp = 30

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "climate", "Ventilasjon")
        self._attr_icon = "mdi:hvac"

    @property
    def current_temperature(self) -> float | None:
        """Return current supply temperature."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.supply_temp

    @property
    def target_temperature(self) -> float | None:
        """Return target supply setpoint."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.supply_setpoint

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self.coordinator.data is None:
            return HVACMode.OFF
        ahu = self.coordinator.data.ahu_mode
        if ahu == 0:
            return HVACMode.OFF
        return HVACMode.FAN_ONLY

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        if self.coordinator.data is None:
            return None
        return AHU_MODE_TO_PRESET.get(self.coordinator.data.ahu_mode)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        if self.coordinator.data is None:
            return {}
        d = self.coordinator.data
        return {
            "unit_mode": d.unit_mode_name,
            "ahu_mode": d.ahu_mode_name,
            "outdoor_temp": d.outdoor_temp,
            "extract_temp": d.extract_temp,
            "recovery_efficiency": d.recovery_efficiency,
            "saf_flow": d.saf_flow,
            "eaf_flow": d.eaf_flow,
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_ahu_mode(0)
        else:
            await self.coordinator.async_set_ahu_mode(2)  # Auto

    async def async_set_temperature(self, **kwargs) -> None:
        """Set target temperature."""
        temp = kwargs.get("temperature")
        if temp is not None:
            await self.coordinator.async_set_supply_setpoint(temp)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        ahu_mode = PRESET_TO_AHU_MODE.get(preset_mode)
        if ahu_mode is not None:
            await self.coordinator.async_set_ahu_mode(ahu_mode)
