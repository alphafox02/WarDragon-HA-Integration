"""Config flow + options flow for the WarDragon integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigEntryState,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_DRONE_INACTIVITY_TIMEOUT,
    CONF_DRONE_PURGE_AFTER,
    CONF_KIT_OFFLINE_TIMEOUT,
    CONF_MQTT_PREFIX,
    DEFAULT_DRONE_INACTIVITY_TIMEOUT,
    DEFAULT_DRONE_PURGE_AFTER,
    DEFAULT_KIT_OFFLINE_TIMEOUT,
    DEFAULT_MQTT_PREFIX,
    DOMAIN,
    MQTT_PREFIX_RE,
)


def _mqtt_loaded(hass: HomeAssistant) -> bool:
    return any(
        entry.state == ConfigEntryState.LOADED
        for entry in hass.config_entries.async_entries(MQTT_DOMAIN)
    )


class WarDragonConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WarDragon."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if not _mqtt_loaded(self.hass):
            return self.async_abort(reason="mqtt_required")

        errors: dict[str, str] = {}
        if user_input is not None:
            prefix = user_input[CONF_MQTT_PREFIX].strip().strip("/").lower()
            if not MQTT_PREFIX_RE.fullmatch(prefix):
                errors["base"] = "invalid_prefix"
            else:
                await self.async_set_unique_id(f"{DOMAIN}_{prefix}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"WarDragon ({prefix})",
                    data={CONF_MQTT_PREFIX: prefix},
                )

        schema = vol.Schema(
            {vol.Required(CONF_MQTT_PREFIX, default=DEFAULT_MQTT_PREFIX): str}
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return WarDragonOptionsFlow(entry)


class WarDragonOptionsFlow(OptionsFlow):
    """Modern HA (≥2024.12) auto-injects `self.config_entry`; older versions
    fall through to the entry passed via `async_get_options_flow`."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry  # fallback for HA < 2024.12

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = getattr(self, "config_entry", None) or self._entry
        opts = entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DRONE_INACTIVITY_TIMEOUT,
                    default=opts.get(CONF_DRONE_INACTIVITY_TIMEOUT, DEFAULT_DRONE_INACTIVITY_TIMEOUT),
                ): vol.All(int, vol.Range(min=10, max=3600)),
                vol.Required(
                    CONF_DRONE_PURGE_AFTER,
                    default=opts.get(CONF_DRONE_PURGE_AFTER, DEFAULT_DRONE_PURGE_AFTER),
                ): vol.All(int, vol.Range(min=60, max=604800)),
                vol.Required(
                    CONF_KIT_OFFLINE_TIMEOUT,
                    default=opts.get(CONF_KIT_OFFLINE_TIMEOUT, DEFAULT_KIT_OFFLINE_TIMEOUT),
                ): vol.All(int, vol.Range(min=10, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
