"""Number entities for Systemair Topvex."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex number entities."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TopvexSupplySetpoint(coordinator),
        TopvexFanOutputNumber(coordinator, "saf", "SAF manuell utgang"),
        TopvexFanOutputNumber(coordinator, "eaf", "EAF manuell utgang"),
        TopvexBypassOutput(coordinator),
    ])


class TopvexSupplySetpoint(TopvexEntity, NumberEntity):
    """Supply air temperature setpoint."""

    _attr_native_min_value = 10.0
    _attr_native_max_value = 30.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "supply_setpoint", "Tilluft settpunkt")

    @property
    def native_value(self) -> float | None:
        """Return current setpoint."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.supply_setpoint

    async def async_set_native_value(self, value: float) -> None:
        """Set supply temperature setpoint."""
        await self.coordinator.async_set_supply_setpoint(value)


class TopvexFanOutputNumber(TopvexEntity, NumberEntity):
    """Fan manual output percentage."""

    _attr_native_min_value = 25
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:fan"

    def __init__(
        self, coordinator: TopvexCoordinator, fan_id: str, name: str
    ) -> None:
        super().__init__(coordinator, f"{fan_id}_manual_output", name)
        self._fan_id = fan_id

    @property
    def native_value(self) -> float | None:
        """Return current manual output."""
        if self.coordinator.data is None:
            return None
        if self._fan_id == "saf":
            return self.coordinator.data.saf_manual_output
        return self.coordinator.data.eaf_manual_output

    async def async_set_native_value(self, value: float) -> None:
        """Set manual output."""
        if self._fan_id == "saf":
            await self.coordinator.async_set_saf_manual_output(value)
        else:
            await self.coordinator.async_set_eaf_manual_output(value)


class TopvexBypassOutput(TopvexEntity, NumberEntity):
    """Bypass manual output percentage."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 10
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:valve"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "bypass_output", "Bypass manuell utgang")

    @property
    def native_value(self) -> float | None:
        """Return current bypass output."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.bypass_manual_output

    async def async_set_native_value(self, value: float) -> None:
        """Set bypass output."""
        await self.coordinator.async_set_bypass_output(value)
