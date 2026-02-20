"""Select entities for Systemair Topvex."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AHU_MODES, AHU_MODE_TO_VALUE, DOMAIN, FAN_MODES, FAN_MODE_TO_VALUE
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex select entities."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TopvexAhuModeSelect(coordinator),
        TopvexFanModeSelect(coordinator, "saf", "Tilluftvifte modus"),
        TopvexFanModeSelect(coordinator, "eaf", "Avtrekksvifte modus"),
    ])


class TopvexAhuModeSelect(TopvexEntity, SelectEntity):
    """AHU operating mode selector."""

    _attr_options = list(AHU_MODES.values())
    _attr_icon = "mdi:hvac"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "ahu_mode", "AHU-modus")

    @property
    def current_option(self) -> str | None:
        """Return current AHU mode."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.ahu_mode_name

    async def async_select_option(self, option: str) -> None:
        """Set AHU mode."""
        value = AHU_MODE_TO_VALUE.get(option)
        if value is not None:
            await self.coordinator.async_set_ahu_mode(value)


class TopvexFanModeSelect(TopvexEntity, SelectEntity):
    """Fan mode selector for SAF or EAF."""

    _attr_options = list(FAN_MODES.values())
    _attr_icon = "mdi:fan-auto"

    def __init__(
        self, coordinator: TopvexCoordinator, fan_id: str, name: str
    ) -> None:
        super().__init__(coordinator, f"{fan_id}_mode", name)
        self._fan_id = fan_id

    @property
    def current_option(self) -> str | None:
        """Return current fan mode."""
        if self.coordinator.data is None:
            return None
        if self._fan_id == "saf":
            return self.coordinator.data.saf_mode_name
        return self.coordinator.data.eaf_mode_name

    async def async_select_option(self, option: str) -> None:
        """Set fan mode."""
        value = FAN_MODE_TO_VALUE.get(option)
        if value is None:
            return
        if self._fan_id == "saf":
            await self.coordinator.async_set_saf_mode(value)
        else:
            await self.coordinator.async_set_eaf_mode(value)
