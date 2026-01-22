"""Config flow for LG Soundbar integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    from .temescal import Temescal
    
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    
    # Try to connect to the soundbar
    device = Temescal(host, port=port, loop=hass.loop)
    
    try:
        connected = await asyncio.wait_for(device.connect(), timeout=10.0)
        if not connected:
            raise CannotConnect
        await device.disconnect()
    except asyncio.TimeoutError:
        raise CannotConnect
    except Exception:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect
    
    return {"title": data.get(CONF_NAME, DEFAULT_NAME)}


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class LGSoundbarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LG Soundbar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
