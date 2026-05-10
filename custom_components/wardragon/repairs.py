"""Repair issue helpers for WarDragon."""

from __future__ import annotations

from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

ISSUE_MQTT_NOT_LOADED = "mqtt_not_loaded"
ISSUE_DRAGONSYNC_NATIVE_MODE_OFF = "dragonsync_native_mode_off"


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


def async_warn_dragonsync_native_mode(hass: HomeAssistant) -> None:
    """Suggest the operator enables DragonSync's `mqtt_ha_native_mode` flag.

    Triggered when we observe `homeassistant/*` discovery configs from
    DragonSync co-existing with this integration's entities. We can't observe
    those topics ourselves (we don't subscribe to `homeassistant/*`), so this
    is currently informational only — kept here so Phase 3+ can wire detection
    once the DragonSync MQTT_HA_NATIVE_MODE flag lands.
    """
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_DRAGONSYNC_NATIVE_MODE_OFF,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_DRAGONSYNC_NATIVE_MODE_OFF,
    )


def async_clear_dragonsync_native_mode_warning(hass: HomeAssistant) -> None:
    ir.async_delete_issue(hass, DOMAIN, ISSUE_DRAGONSYNC_NATIVE_MODE_OFF)
