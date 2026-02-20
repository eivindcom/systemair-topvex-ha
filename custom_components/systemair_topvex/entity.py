"""Base entity for Systemair Topvex."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TopvexCoordinator, TopvexData


class TopvexEntity(CoordinatorEntity[TopvexCoordinator]):
    """Base entity for Topvex devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TopvexCoordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.client.host}_{key}"
        self._attr_translation_key = key
        self._attr_name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.client.host)},
            name="Topvex TC/C03 EL CAV",
            manufacturer="Systemair",
            model="Topvex TC/C03 EL CAV",
            sw_version="Access v4.6-1-00",
            configuration_url=f"http://{self.coordinator.client.host}",
        )

    @property
    def topvex_data(self) -> TopvexData:
        """Return current Topvex data."""
        return self.coordinator.data
