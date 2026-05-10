"""The WarDragon integration."""

from __future__ import annotations

import logging

from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_MQTT_PREFIX, DOMAIN
from .coordinator import WarDragonCoordinator
from .frontend import async_register_frontend
from .mqtt_client import WarDragonMQTTSubscriber
from .repairs import async_check_mqtt_loaded
from .services import async_ensure_services, async_release_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.BUTTON,
]


def _mqtt_loaded(hass: HomeAssistant) -> bool:
    return any(
        e.state == ConfigEntryState.LOADED
        for e in hass.config_entries.async_entries(MQTT_DOMAIN)
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WarDragon from a config entry."""
    async_check_mqtt_loaded(hass)
    if not _mqtt_loaded(hass):
        raise ConfigEntryNotReady("MQTT integration not loaded")

    await async_register_frontend(hass)

    coordinator = WarDragonCoordinator(hass, entry)
    subscriber = WarDragonMQTTSubscriber(hass, coordinator, entry.data[CONF_MQTT_PREFIX])

    try:
        await coordinator.async_setup()
        await subscriber.async_setup()
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
            "coordinator": coordinator,
            "mqtt": subscriber,
        }
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        # Setup failed: HA will not call async_unload_entry, so clean up here.
        try:
            await subscriber.async_unload()
        except Exception:
            _LOGGER.debug("subscriber cleanup after failed setup", exc_info=True)
        try:
            await coordinator.async_shutdown()
        except Exception:
            _LOGGER.debug("coordinator cleanup after failed setup", exc_info=True)
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        raise

    await async_ensure_services(hass)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["mqtt"].async_unload()
        await data["coordinator"].async_shutdown()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
        await async_release_services(hass)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
