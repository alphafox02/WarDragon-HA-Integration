"""Custom services for the WarDragon integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .const import DOMAIN

SERVICE_CLEAR_DRONE = "clear_drone"
SERVICE_EXPORT_DRONES = "export_drones"

CLEAR_DRONE_SCHEMA = vol.Schema(
    {
        vol.Required("drone_id"): vol.All(str, vol.Length(min=1)),
    }
)

EXPORT_DRONES_SCHEMA = vol.Schema({})


def _coordinators(hass: HomeAssistant) -> list:
    return [
        bucket["coordinator"]
        for bucket in (hass.data.get(DOMAIN, {}) or {}).values()
        if isinstance(bucket, dict) and "coordinator" in bucket
    ]


async def async_ensure_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_CLEAR_DRONE):
        return

    async def _clear_drone(call: ServiceCall) -> None:
        drone_id: str = call.data["drone_id"]
        coordinators = _coordinators(hass)
        if not coordinators:
            raise HomeAssistantError("No WarDragon integration is loaded.")
        cleared = False
        for coord in coordinators:
            if await coord.async_clear_drone(drone_id):
                cleared = True
        if not cleared:
            raise ServiceValidationError(f"Drone {drone_id!r} not found in any WarDragon entry.")

    async def _export_drones(call: ServiceCall) -> ServiceResponse:
        coordinators = _coordinators(hass)
        if not coordinators:
            raise HomeAssistantError("No WarDragon integration is loaded.")
        drones: list[dict[str, Any]] = []
        for coord in coordinators:
            drones.extend(await coord.async_export_drones())
        return {"count": len(drones), "drones": drones}

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_DRONE,
        _clear_drone,
        schema=CLEAR_DRONE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_DRONES,
        _export_drones,
        schema=EXPORT_DRONES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


async def async_release_services(hass: HomeAssistant) -> None:
    """Remove services when the last config entry is unloaded."""
    has_loaded_entry = any(
        entry.state == ConfigEntryState.LOADED
        for entry in hass.config_entries.async_entries(DOMAIN)
    )
    if has_loaded_entry:
        return
    if hass.services.has_service(DOMAIN, SERVICE_CLEAR_DRONE):
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR_DRONE)
    if hass.services.has_service(DOMAIN, SERVICE_EXPORT_DRONES):
        hass.services.async_remove(DOMAIN, SERVICE_EXPORT_DRONES)
