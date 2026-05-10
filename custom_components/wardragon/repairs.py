"""Repair issue helpers for WarDragon."""

from __future__ import annotations

from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

ISSUE_MQTT_NOT_LOADED = "mqtt_not_loaded"
ISSUE_DRAGONSYNC_HA_ENABLED_ON = "dragonsync_ha_enabled_on"


def _mqtt_loaded(hass: HomeAssistant) -> bool:
    return any(
        entry.state == ConfigEntryState.LOADED
        for entry in hass.config_entries.async_entries(MQTT_DOMAIN)
    )


def async_check_mqtt_loaded(hass: HomeAssistant) -> None:
    if _mqtt_loaded(hass):
        ir.async_delete_issue(hass, DOMAIN, ISSUE_MQTT_NOT_LOADED)
        return
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_MQTT_NOT_LOADED,
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        translation_key=ISSUE_MQTT_NOT_LOADED,
    )


def async_warn_dragonsync_ha_enabled(hass: HomeAssistant) -> None:
    """Suggest the operator turns DragonSync's `mqtt_ha_enabled` off.

    Triggered when we observe `homeassistant/*` discovery configs from
    DragonSync co-existing with this integration's entities (which produces
    duplicates). We currently don't subscribe to `homeassistant/*`, so this
    helper is informational scaffolding for future detection; the strings
    entry exists so the repair issue renders correctly when wired up.
    """
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_DRAGONSYNC_HA_ENABLED_ON,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_DRAGONSYNC_HA_ENABLED_ON,
    )


def async_clear_dragonsync_ha_enabled_warning(hass: HomeAssistant) -> None:
    ir.async_delete_issue(hass, DOMAIN, ISSUE_DRAGONSYNC_HA_ENABLED_ON)
