"""Button entities for Systemair Topvex."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BOOST_DEFAULT_MINUTES, DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex buttons."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TopvexAcknowledgeAlarmsButton(coordinator),
        TopvexResetFilterButton(coordinator),
        TopvexKitchenBoostButton(coordinator, 10),
        TopvexKitchenBoostButton(coordinator, 20),
        TopvexKitchenBoostButton(coordinator, 30),
        TopvexCancelBoostButton(coordinator),
    ])


class TopvexAcknowledgeAlarmsButton(TopvexEntity, ButtonEntity):
    """Button to acknowledge all alarms."""

    _attr_icon = "mdi:alarm-check"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "acknowledge_alarms", "Kvitter alarmer")

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_acknowledge_alarms()


class TopvexResetFilterButton(TopvexEntity, ButtonEntity):
    """Button to reset filter alarm."""

    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "reset_filter", "Nullstill filteralarm")

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_reset_filter_alarm()


class TopvexKitchenBoostButton(TopvexEntity, ButtonEntity):
    """Button to start kitchen boost."""

    _attr_icon = "mdi:fan-plus"

    def __init__(self, coordinator: TopvexCoordinator, minutes: int) -> None:
        super().__init__(
            coordinator,
            f"kitchen_boost_{minutes}",
            f"Komfyravtrekk {minutes} min",
        )
        self._minutes = minutes

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_start_kitchen_boost(self._minutes)


class TopvexCancelBoostButton(TopvexEntity, ButtonEntity):
    """Button to cancel kitchen boost."""

    _attr_icon = "mdi:fan-off"

    def __init__(self, coordinator: TopvexCoordinator) -> None:
        super().__init__(coordinator, "cancel_boost", "Avbryt komfyravtrekk")

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_cancel_kitchen_boost()
