"""Systemair Topvex Ventilation integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol

from .const import (
    BOOST_DEFAULT_MINUTES,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import TopvexCoordinator
from .modbus_client import TopvexModbusClient

_LOGGER = logging.getLogger(__name__)

SERVICE_KITCHEN_BOOST = "kitchen_boost"
SERVICE_CANCEL_BOOST = "cancel_kitchen_boost"

KITCHEN_BOOST_SCHEMA = vol.Schema({
    vol.Optional("minutes", default=BOOST_DEFAULT_MINUTES): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=60)
    ),
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Systemair Topvex from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    unit_id = entry.data.get("unit_id", DEFAULT_UNIT_ID)

    client = TopvexModbusClient(host, port, unit_id)
    coordinator = TopvexCoordinator(hass, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_kitchen_boost(call: ServiceCall) -> None:
        minutes = call.data.get("minutes", BOOST_DEFAULT_MINUTES)
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, TopvexCoordinator):
                await coord.async_start_kitchen_boost(minutes)

    async def handle_cancel_boost(call: ServiceCall) -> None:
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, TopvexCoordinator):
                await coord.async_cancel_kitchen_boost()

    hass.services.async_register(
        DOMAIN, SERVICE_KITCHEN_BOOST, handle_kitchen_boost,
        schema=KITCHEN_BOOST_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CANCEL_BOOST, handle_cancel_boost,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: TopvexCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.disconnect()

    # Remove services if no entries remain
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_KITCHEN_BOOST)
        hass.services.async_remove(DOMAIN, SERVICE_CANCEL_BOOST)

    return unload_ok
