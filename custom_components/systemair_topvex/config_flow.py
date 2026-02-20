"""Config flow for Systemair Topvex."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT_ID, DOMAIN
from .modbus_client import TopvexModbusClient

_LOGGER = logging.getLogger(__name__)


class TopvexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Systemair Topvex."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            unit_id = user_input.get("unit_id", DEFAULT_UNIT_ID)

            # Test connection by reading unit mode register
            client = TopvexModbusClient(host, port, unit_id)
            try:
                connected = await client.connect()
                if connected:
                    result = await client.read_input_registers(396, 1)
                    await client.disconnect()
                    if result is not None:
                        await self.async_set_unique_id(host)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=f"Topvex ({host})",
                            data=user_input,
                        )
                    errors["base"] = "cannot_read"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Error connecting to Topvex")
                errors["base"] = "cannot_connect"
            finally:
                await client.disconnect()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="192.168.1.84"): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional("unit_id", default=DEFAULT_UNIT_ID): int,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
            }),
            errors=errors,
        )
