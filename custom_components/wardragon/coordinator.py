"""WarDragon coordinator: owns kit + drone state, lifecycle, multi-kit fusion."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DRONE_INACTIVITY_TIMEOUT,
    CONF_DRONE_PURGE_AFTER,
    CONF_KIT_OFFLINE_TIMEOUT,
    CONF_MQTT_PREFIX,
    DEFAULT_DRONE_INACTIVITY_TIMEOUT,
    DEFAULT_DRONE_PURGE_AFTER,
    DEFAULT_KIT_OFFLINE_TIMEOUT,
    DOMAIN,
    EVENT_DRONE_DETECTED,
    EVENT_DRONE_LOST,
    EVENT_DRONE_PURGED,
    EVENT_KIT_OFFLINE,
    EVENT_SIGNAL_DETECTED,
    SIGNAL_NEW_DRONE,
    SIGNAL_NEW_KIT,
    SIGNAL_NEW_KIT_SIGNAL_CHANNEL,
    STORAGE_VERSION,
    drone_update_signal,
    kit_signal_update_signal,
    kit_update_signal,
)
from .models import Drone, Kit, Signal

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

HOUSEKEEPING_INTERVAL = timedelta(seconds=10)


class WarDragonCoordinator:
    """Single source of truth for kits and drones.

    Drones may be observed by multiple kits; the coordinator merges per-kit
    payloads via `Drone.merged_with`, taking position from whichever kit has
    the strongest RSSI and tracking per-kit RSSIs as `rssi_by_kit`.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._prefix: str = entry.data[CONF_MQTT_PREFIX]
        self._store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self._kits: dict[str, Kit] = {}
        self._drones: dict[str, Drone] = {}
        self._kit_signals: dict[str, Signal] = {}
        self._pending_kit_availability: dict[str, bool] = {}
        self._signal_channels: set[str] = set()
        self._dirty = False
        self._cancel_interval: CALLBACK_TYPE | None = None

    @property
    def mqtt_prefix(self) -> str:
        return self._prefix

    def get_kit(self, kit_id: str) -> Kit | None:
        return self._kits.get(kit_id)

    def get_drone(self, drone_id: str) -> Drone | None:
        return self._drones.get(drone_id)

    def get_all_kits(self) -> list[Kit]:
        return list(self._kits.values())

    def get_all_drones(self) -> list[Drone]:
        return list(self._drones.values())

    def get_kit_signal(self, kit_id: str) -> Signal | None:
        return self._kit_signals.get(kit_id)

    def get_signal_channels(self) -> list[str]:
        return list(self._signal_channels)

    def option_drone_inactivity_timeout(self) -> int:
        return int(self.entry.options.get(CONF_DRONE_INACTIVITY_TIMEOUT, DEFAULT_DRONE_INACTIVITY_TIMEOUT))

    def option_drone_purge_after(self) -> int:
        return int(self.entry.options.get(CONF_DRONE_PURGE_AFTER, DEFAULT_DRONE_PURGE_AFTER))

    def option_kit_offline_timeout(self) -> int:
        return int(self.entry.options.get(CONF_KIT_OFFLINE_TIMEOUT, DEFAULT_KIT_OFFLINE_TIMEOUT))

    async def async_setup(self) -> None:
        await self._async_load_store()
        self._cancel_interval = async_track_time_interval(
            self.hass, self._async_housekeeping, HOUSEKEEPING_INTERVAL
        )

    async def async_shutdown(self) -> None:
        if self._cancel_interval is not None:
            self._cancel_interval()
            self._cancel_interval = None
        await self._async_save_store_if_dirty()

    async def async_handle_drone_payload(self, payload: dict[str, Any], *, retained: bool) -> None:
        parsed = Drone.from_drone_payload(payload)
        if parsed is None:
            return

        now = dt_util.utcnow()
        if retained and parsed.observed_at is not None:
            try:
                ts = dt_util.utc_from_timestamp(parsed.observed_at)
                received_at = min(ts, now)
            except (OSError, ValueError):
                received_at = now
        else:
            received_at = now

        new_drone = parsed.with_last_seen(received_at, received_at).with_availability(True)
        existing = self._drones.get(parsed.drone_id)
        if existing is None:
            self._drones[parsed.drone_id] = new_drone
            async_dispatcher_send(self.hass, SIGNAL_NEW_DRONE, parsed.drone_id)
            self.hass.bus.async_fire(
                EVENT_DRONE_DETECTED,
                {"drone_id": parsed.drone_id, "seen_by": parsed.seen_by},
            )
            _LOGGER.debug("New drone detected: %s (seen_by=%s)", parsed.drone_id, parsed.seen_by)
        else:
            self._drones[parsed.drone_id] = existing.merged_with(new_drone)

        async_dispatcher_send(self.hass, drone_update_signal(parsed.drone_id))
        self._dirty = True

    async def async_handle_system_attrs(self, payload: dict[str, Any], *, retained: bool) -> None:
        parsed = Kit.from_attrs_payload(payload)
        if parsed is None:
            return

        now = dt_util.utcnow()
        is_new = parsed.kit_id not in self._kits
        availability = self._pending_kit_availability.pop(parsed.kit_id, True)
        kit = parsed.with_last_seen(now).with_availability(availability)
        self._kits[parsed.kit_id] = kit
        if is_new:
            async_dispatcher_send(self.hass, SIGNAL_NEW_KIT, parsed.kit_id)
            _LOGGER.debug("New kit registered: %s", parsed.kit_id)
        async_dispatcher_send(self.hass, kit_update_signal(parsed.kit_id))
        self._dirty = True

    async def async_handle_system_availability(self, kit_id: str, online: bool) -> None:
        existing = self._kits.get(kit_id)
        if existing is None:
            self._pending_kit_availability[kit_id] = online
            return
        if existing.available == online:
            return
        self._kits[kit_id] = existing.with_availability(online)
        async_dispatcher_send(self.hass, kit_update_signal(kit_id))
        if not online:
            self.hass.bus.async_fire(EVENT_KIT_OFFLINE, {"kit_id": kit_id})

    async def async_handle_signal_payload(self, payload: dict[str, Any], *, retained: bool) -> None:
        parsed = Signal.from_payload(payload)
        if parsed is None:
            return
        now = dt_util.utcnow()
        if retained and parsed.observed_at is not None:
            try:
                ts = dt_util.utc_from_timestamp(parsed.observed_at)
                received_at = min(ts, now)
            except (OSError, ValueError):
                received_at = now
        else:
            received_at = now
        signal = parsed.with_last_seen(received_at, received_at)

        kit_id = signal.seen_by
        if kit_id is not None:
            is_new_channel = kit_id not in self._signal_channels
            self._kit_signals[kit_id] = signal
            self._signal_channels.add(kit_id)
            if is_new_channel:
                async_dispatcher_send(self.hass, SIGNAL_NEW_KIT_SIGNAL_CHANNEL, kit_id)
            async_dispatcher_send(self.hass, kit_signal_update_signal(kit_id))

        self.hass.bus.async_fire(
            EVENT_SIGNAL_DETECTED,
            {
                "uid": signal.uid,
                "signal_type": signal.signal_type,
                "source": signal.source,
                "callsign": signal.callsign,
                "description": signal.description,
                "center_mhz": signal.center_mhz,
                "bandwidth_mhz": signal.bandwidth_mhz,
                "rssi": signal.rssi,
                "lat": signal.lat,
                "lon": signal.lon,
                "alt": signal.alt,
                "radius_m": signal.radius_m,
                "seen_by": signal.seen_by,
                "observed_at": signal.observed_at,
            },
        )

    async def async_handle_service_availability(self, kit_id: str, online: bool) -> None:
        _LOGGER.info(
            "DragonSync service availability for %s: %s",
            kit_id,
            "online" if online else "offline",
        )
        if not online:
            self.hass.bus.async_fire(EVENT_KIT_OFFLINE, {"kit_id": kit_id, "via": "service"})

    async def async_clear_drone(self, drone_id: str) -> bool:
        if drone_id not in self._drones:
            return False
        await self._async_purge_drone(drone_id)
        return True

    async def async_export_drones(self) -> list[dict[str, Any]]:
        return [
            {
                "id": d.drone_id,
                "description": d.description,
                "latitude": d.latitude,
                "longitude": d.longitude,
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
                "rid_make": d.rid_make,
                "rid_model": d.rid_model,
                "rid_status": d.rid_status,
                "seen_by": d.seen_by,
                "rssi_by_kit": dict(d.rssi_by_kit),
                "available": d.available,
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            }
            for d in self._drones.values()
        ]

    async def _async_purge_drone(self, drone_id: str) -> None:
        self._drones.pop(drone_id, None)
        # Drop the device from the registry; HA cascades entity removal
        # automatically. No need to dispatch per-entity removal.
        try:
            device_reg = dr.async_get(self.hass)
            device = device_reg.async_get_device(identifiers={(DOMAIN, f"drone:{drone_id}")})
            if device is not None:
                device_reg.async_update_device(
                    device.id, remove_config_entry_id=self.entry.entry_id
                )
        except Exception:
            _LOGGER.debug("Device registry purge failed for %s", drone_id, exc_info=True)
        self.hass.bus.async_fire(EVENT_DRONE_PURGED, {"drone_id": drone_id})
        self._dirty = True

    async def _async_housekeeping(self, now: datetime | None = None) -> None:
        now = now or dt_util.utcnow()
        inactivity = self.option_drone_inactivity_timeout()
        purge_after = self.option_drone_purge_after()
        kit_offline = self.option_kit_offline_timeout()

        for drone_id in list(self._drones):
            drone = self._drones[drone_id]
            ref = drone.received_at or drone.last_seen
            if ref is None:
                continue
            age_s = (now - ref).total_seconds()
            if age_s > purge_after:
                _LOGGER.info("Purging drone %s (age %ds > purge_after=%ds)", drone_id, int(age_s), purge_after)
                await self._async_purge_drone(drone_id)
                continue
            if age_s > inactivity and drone.available:
                self._drones[drone_id] = drone.with_availability(False)
                async_dispatcher_send(self.hass, drone_update_signal(drone_id))
                self.hass.bus.async_fire(EVENT_DRONE_LOST, {"drone_id": drone_id})

        for kit_id in list(self._kits):
            kit = self._kits[kit_id]
            ref = kit.last_seen
            if ref is None:
                continue
            age_s = (now - ref).total_seconds()
            if age_s > kit_offline and kit.available:
                self._kits[kit_id] = kit.with_availability(False)
                async_dispatcher_send(self.hass, kit_update_signal(kit_id))
                self.hass.bus.async_fire(EVENT_KIT_OFFLINE, {"kit_id": kit_id, "via": "heartbeat"})

        await self._async_save_store_if_dirty()

    async def _async_load_store(self) -> None:
        try:
            data = await self._store.async_load()
        except Exception:
            _LOGGER.debug("Store load failed", exc_info=True)
            return
        if not isinstance(data, dict):
            return
        for kit_id in data.get("kits", []) or []:
            if isinstance(kit_id, str) and kit_id:
                self._kits[kit_id] = Kit.restore_placeholder(kit_id)
        for record in data.get("drones", []) or []:
            if not isinstance(record, dict):
                continue
            drone_id = record.get("id")
            if not isinstance(drone_id, str) or not drone_id:
                continue
            last_seen_iso = record.get("last_seen")
            last_seen = None
            if isinstance(last_seen_iso, str):
                try:
                    last_seen = datetime.fromisoformat(last_seen_iso)
                except ValueError:
                    last_seen = None
            self._drones[drone_id] = Drone.restore_placeholder(drone_id, last_seen)

    async def _async_save_store_if_dirty(self) -> None:
        if not self._dirty:
            return
        data = {
            "kits": list(self._kits.keys()),
            "drones": [
                {
                    "id": d.drone_id,
                    "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                }
                for d in self._drones.values()
            ],
        }
        try:
            await self._store.async_save(data)
            self._dirty = False
        except Exception:
            _LOGGER.debug("Store save failed", exc_info=True)
