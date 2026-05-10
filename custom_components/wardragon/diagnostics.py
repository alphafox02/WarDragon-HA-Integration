"""Diagnostics for the WarDragon integration."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator

REDACT = {"operator_id", "caa_id", "mac", "seen_by"}


def _hash_kit_id(kit_id: str) -> str:
    return f"kit-{hashlib.sha1(kit_id.encode()).hexdigest()[:8]}"


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    bucket = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator: WarDragonCoordinator | None = bucket.get("coordinator")
    if coordinator is None:
        return {"error": "coordinator not loaded"}

    kits = [
        {
            "kit_id": k.kit_id,
            "available": k.available,
            "gps_fix": k.gps_fix,
            "has_position": k.has_position,
            "cpu_usage": k.cpu_usage,
            "memory_available_mb": k.memory_available_mb,
            "uptime_s": k.uptime_s,
            "pluto_temp_c": k.pluto_temp_c,
            "zynq_temp_c": k.zynq_temp_c,
            "last_seen": k.last_seen.isoformat() if k.last_seen else None,
        }
        for k in coordinator.get_all_kits()
    ]
    drones = [
        async_redact_data(
            {
                "drone_id": d.drone_id,
                "description": d.description,
                "track_type": d.track_type,
                "available": d.available,
                "has_position": d.has_position,
                "altitude": d.alt,
                "speed": d.speed,
                "rssi": d.rssi,
                "freq_mhz": d.freq_mhz,
                "transport": d.transport,
                "protocol_family": d.protocol_family,
                "freq_band": d.freq_band,
                "ua_type_name": d.ua_type_name,
                "operator_id": d.operator_id,
                "caa_id": d.caa_id,
                "mac": d.mac,
                "rid_make": d.rid_make,
                "rid_model": d.rid_model,
                "rid_status": d.rid_status,
                "rid_lookup_success": d.rid_lookup_success,
                "seen_by": d.seen_by,
                "rssi_by_kit": {_hash_kit_id(k): v for k, v in d.rssi_by_kit.items()},
                "kit_count": len(d.rssi_by_kit),
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            },
            REDACT,
        )
        for d in coordinator.get_all_drones()
    ]
    return {
        "entry": {
            "title": entry.title,
            "data": {"mqtt_prefix": entry.data.get("mqtt_prefix")},
            "options": dict(entry.options),
        },
        "summary": {
            "kit_count": len(kits),
            "drone_count": len(drones),
        },
        "kits": kits,
        "drones": drones,
    }
