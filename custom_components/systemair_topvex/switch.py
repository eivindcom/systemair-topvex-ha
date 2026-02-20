"""Switch entities for Systemair Topvex."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex switches."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TopvexBypassSwitch(coordinator)])


class TopvexBypassSwitch(TopvexEntity, SwitchEntity):
    """Bypass manual mode switch."""

    _attr_icon = "mdi:valve"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "bypass_manual", "Bypass manuell modus")

    @property
    def is_on(self) -> bool | None:
        """Return True if bypass is in manual mode."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.bypass_mode == 1

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        if self.coordinator.data is None:
            return {}
        return {
            "bypass_value": self.coordinator.data.seq_b,
            "bypass_manual_output": self.coordinator.data.bypass_manual_output,
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Set bypass to manual mode."""
        await self.coordinator.async_set_bypass_mode(1)

    async def async_turn_off(self, **kwargs) -> None:
        """Set bypass to auto mode."""
        await self.coordinator.async_set_bypass_mode(0)
