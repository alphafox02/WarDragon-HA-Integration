"""Device trackers for WarDragon kits and drones."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SIGNAL_NEW_DRONE,
    SIGNAL_NEW_KIT,
    SIGNAL_NEW_KIT_SIGNAL_CHANNEL,
)
from .entity import WarDragonDroneEntity, WarDragonKitEntity, WarDragonKitSignalEntity

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator

_LOGGER = logging.getLogger(__name__)

DRONE_TRACKER_DESC = EntityDescription(
    key="position",
    translation_key="drone_position",
    name="Position",
)
PILOT_TRACKER_DESC = EntityDescription(
    key="pilot_position",
    translation_key="pilot_position",
    name="Pilot",
)
HOME_TRACKER_DESC = EntityDescription(
    key="home_position",
    translation_key="home_position",
    name="Home",
)
KIT_TRACKER_DESC = EntityDescription(
    key="position",
    translation_key="kit_position",
    name="Position",
)
SIGNAL_TRACKER_DESC = EntityDescription(
    key="signal_position",
    translation_key="signal_position",
    name="Current signal",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WarDragonCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    seen_kits: set[str] = set()
    seen_drones: set[str] = set()
    seen_signal_channels: set[str] = set()

    def _drone_entities(drone_id: str) -> list:
        return [
            WarDragonDroneDeviceTracker(coordinator, drone_id, DRONE_TRACKER_DESC),
            WarDragonPilotDeviceTracker(coordinator, drone_id, PILOT_TRACKER_DESC),
            WarDragonHomeDeviceTracker(coordinator, drone_id, HOME_TRACKER_DESC),
        ]

    initial: list = []
    for kit in coordinator.get_all_kits():
        if kit.kit_id not in seen_kits:
            seen_kits.add(kit.kit_id)
            initial.append(WarDragonKitDeviceTracker(coordinator, kit.kit_id, KIT_TRACKER_DESC))
    for drone in coordinator.get_all_drones():
        if drone.drone_id not in seen_drones:
            seen_drones.add(drone.drone_id)
            initial.extend(_drone_entities(drone.drone_id))
    for kit_id in coordinator.get_signal_channels():
        if kit_id not in seen_signal_channels:
            seen_signal_channels.add(kit_id)
            initial.append(WarDragonSignalDeviceTracker(coordinator, kit_id, SIGNAL_TRACKER_DESC))
    if initial:
        async_add_entities(initial)

    @callback
    def _on_new_kit(kit_id: str) -> None:
        if kit_id in seen_kits:
            return
        seen_kits.add(kit_id)
        async_add_entities([WarDragonKitDeviceTracker(coordinator, kit_id, KIT_TRACKER_DESC)])

    @callback
    def _on_new_drone(drone_id: str) -> None:
        if drone_id in seen_drones:
            return
        seen_drones.add(drone_id)
        async_add_entities(_drone_entities(drone_id))

    @callback
    def _on_new_signal_channel(kit_id: str) -> None:
        if kit_id in seen_signal_channels:
            return
        seen_signal_channels.add(kit_id)
        async_add_entities(
            [WarDragonSignalDeviceTracker(coordinator, kit_id, SIGNAL_TRACKER_DESC)]
        )

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_KIT, _on_new_kit))
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_DRONE, _on_new_drone))
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_NEW_KIT_SIGNAL_CHANNEL, _on_new_signal_channel)
    )


class WarDragonDroneDeviceTracker(WarDragonDroneEntity, TrackerEntity):
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:quadcopter"

    @property
    def latitude(self) -> float | None:
        d = self.drone
        return d.latitude if d and d.has_position else None

    @property
    def longitude(self) -> float | None:
        d = self.drone
        return d.longitude if d and d.has_position else None

    @property
    def location_accuracy(self) -> int:
        return 0

    @property
    def available(self) -> bool:
        d = self.drone
        return d is not None and d.available and d.has_position

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.drone
        if d is None:
            return {}
        attrs: dict[str, Any] = {
            "altitude": d.alt,
            "height": d.height,
            "speed": d.speed,
            "vspeed": d.vspeed,
            "direction": d.direction,
            "rssi": d.rssi,
            "description": d.description,
            "seen_by": d.seen_by,
            "freq_mhz": d.freq_mhz,
            "transport": d.transport,
            "protocol_family": d.protocol_family,
            "freq_band": d.freq_band,
            "drone_class": d.drone_class,
            "ua_type_name": d.ua_type_name,
            "operator_id": d.operator_id,
            "caa_id": d.caa_id,
        }
        if d.has_pilot:
            attrs["pilot_latitude"] = d.pilot_lat
            attrs["pilot_longitude"] = d.pilot_lon
        if d.has_home:
            attrs["home_latitude"] = d.home_lat
            attrs["home_longitude"] = d.home_lon
        if d.rssi_by_kit:
            attrs["rssi_by_kit"] = dict(d.rssi_by_kit)
            attrs["kit_count"] = len(d.rssi_by_kit)
        return {k: v for k, v in attrs.items() if v is not None}


class WarDragonPilotDeviceTracker(WarDragonDroneEntity, TrackerEntity):
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:account-star"

    @property
    def latitude(self) -> float | None:
        d = self.drone
        return d.pilot_lat if d and d.has_pilot else None

    @property
    def longitude(self) -> float | None:
        d = self.drone
        return d.pilot_lon if d and d.has_pilot else None

    @property
    def location_accuracy(self) -> int:
        return 0

    @property
    def available(self) -> bool:
        d = self.drone
        return d is not None and d.available and d.has_pilot


class WarDragonHomeDeviceTracker(WarDragonDroneEntity, TrackerEntity):
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:home-map-marker"

    @property
    def latitude(self) -> float | None:
        d = self.drone
        return d.home_lat if d and d.has_home else None

    @property
    def longitude(self) -> float | None:
        d = self.drone
        return d.home_lon if d and d.has_home else None

    @property
    def location_accuracy(self) -> int:
        return 0

    @property
    def available(self) -> bool:
        d = self.drone
        return d is not None and d.available and d.has_home


class WarDragonKitDeviceTracker(WarDragonKitEntity, TrackerEntity):
    """Kit position tracker.

    Available whenever the kit has valid coordinates (filtered for the
    0,0 sentinel). gps_fix is NOT a gating condition here — modern GPS
    receivers continue to report the last-known fix while temporarily
    losing lock, and the operator still wants the kit visible on the map
    in that case. Fix quality is surfaced via the kit's binary_sensor
    (binary_sensor.<kit>_gps_fix) for operators who care.
    """

    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:router-wireless"

    @property
    def latitude(self) -> float | None:
        k = self.kit
        return k.latitude if k and k.has_position else None

    @property
    def longitude(self) -> float | None:
        k = self.kit
        return k.longitude if k and k.has_position else None

    @property
    def location_accuracy(self) -> int:
        return 0

    @property
    def available(self) -> bool:
        k = self.kit
        return k is not None and k.available and k.has_position

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        k = self.kit
        if k is None:
            return {}
        return {
            kk: vv
            for kk, vv in {
                "hae": k.hae,
                "speed_mps": k.speed_mps,
                "track_deg": k.track_deg,
                "time_source": k.time_source,
                "gpsd_time_utc": k.gpsd_time_utc,
                "gps_fix": k.gps_fix,
            }.items()
            if vv is not None
        }


class WarDragonSignalDeviceTracker(WarDragonKitSignalEntity, TrackerEntity):
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:waveform"

    @property
    def latitude(self) -> float | None:
        s = self.signal
        return s.lat if s and s.has_position else None

    @property
    def longitude(self) -> float | None:
        s = self.signal
        return s.lon if s and s.has_position else None

    @property
    def location_accuracy(self) -> int:
        s = self.signal
        if s is None or s.radius_m is None:
            return 0
        try:
            return int(s.radius_m)
        except (TypeError, ValueError):
            return 0

    @property
    def available(self) -> bool:
        s = self.signal
        return s is not None and s.has_position

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self.signal
        if s is None:
            return {}
        return {
            kk: vv
            for kk, vv in {
                "uid": s.uid,
                "signal_type": s.signal_type,
                "source": s.source,
                "callsign": s.callsign,
                "description": s.description,
                "rssi": s.rssi,
                "center_mhz": s.center_mhz,
                "bandwidth_mhz": s.bandwidth_mhz,
                "radius_m": s.radius_m,
                "seen_by": s.seen_by,
            }.items()
            if vv is not None
        }
