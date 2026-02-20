"""Binary sensor entities for Systemair Topvex alarms."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ALARM_NAMES, ALARM_STATUSES, DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex alarm binary sensors."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensors for known alarms that are likely to appear
    known_alarm_ids = sorted(ALARM_NAMES.keys())
    entities = []
    for alarm_id in known_alarm_ids:
        entities.append(TopvexAlarmSensor(coordinator, alarm_id))

    async_add_entities(entities)


class TopvexAlarmSensor(TopvexEntity, BinarySensorEntity):
    """Binary sensor for a Topvex alarm."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: TopvexCoordinator, alarm_id: int) -> None:
        name = ALARM_NAMES.get(alarm_id, f"Alarm {alarm_id}")
        super().__init__(coordinator, f"alarm_{alarm_id}", name)
        self._alarm_id = alarm_id

    @property
    def is_on(self) -> bool | None:
        """Return True if alarm is active (not OK)."""
        if self.coordinator.data is None:
            return None
        for alarm in self.coordinator.data.alarms:
            if alarm.id == self._alarm_id:
                return True
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return alarm status details."""
        if self.coordinator.data is None:
            return {}
        for alarm in self.coordinator.data.alarms:
            if alarm.id == self._alarm_id:
                return {
                    "status_code": alarm.status,
                    "status_name": alarm.status_name,
                }
        return {"status_code": 1, "status_name": "OK"}

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable most alarms by default, enable common ones."""
        return self._alarm_id in (
            52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 78, 86,
        )
