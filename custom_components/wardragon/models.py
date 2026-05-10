"""Frozen dataclasses representing WarDragon kits and drones.

Strict-but-forgiving validation: drop only on hard schema violations
(missing `id`, wrong `track_type`); everything else is best-effort with
a DEBUG log on parse failures.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)

NO_FIX_LAT = 0.0
NO_FIX_LON = 0.0


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _parse_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _parse_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if s else None


def _parse_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "online"}
    return default


def _truncate_payload_repr(payload: dict[str, Any], limit: int = 200) -> str:
    s = repr(payload)
    return s if len(s) <= limit else s[: limit - 3] + "..."


def _filter_no_fix(lat: float | None, lon: float | None) -> tuple[float | None, float | None]:
    """Map the (0.0, 0.0) sentinel to (None, None) so trackers can gate on has_position."""
    if lat is None or lon is None:
        return lat, lon
    if lat == NO_FIX_LAT and lon == NO_FIX_LON:
        return None, None
    return lat, lon


@dataclass(slots=True, frozen=True)
class Kit:
    """A WarDragon kit (one physical device running DragonSync)."""

    kit_id: str
    latitude: float | None = None
    longitude: float | None = None
    hae: float | None = None
    cpu_usage: float | None = None
    memory_total_mb: float | None = None
    memory_available_mb: float | None = None
    disk_total_mb: float | None = None
    disk_used_mb: float | None = None
    temperature_c: float | None = None
    pluto_temp_c: float | None = None
    zynq_temp_c: float | None = None
    uptime_s: float | None = None
    speed_mps: float | None = None
    track_deg: float | None = None
    gps_fix: bool = False
    time_source: str | None = None
    gpsd_time_utc: str | None = None
    updated: int | None = None

    available: bool = True
    last_seen: datetime | None = None

    @classmethod
    def from_attrs_payload(cls, payload: dict[str, Any]) -> Kit | None:
        if not isinstance(payload, dict):
            _LOGGER.debug("Kit payload not a dict: %s", _truncate_payload_repr({"raw": payload}))
            return None
        kit_id = _parse_str(payload.get("id"))
        if kit_id is None:
            _LOGGER.debug("Kit payload missing id: %s", _truncate_payload_repr(payload))
            return None
        lat, lon = _filter_no_fix(_parse_float(payload.get("latitude")), _parse_float(payload.get("longitude")))
        return cls(
            kit_id=kit_id,
            latitude=lat,
            longitude=lon,
            hae=_parse_float(payload.get("hae")),
            cpu_usage=_parse_float(payload.get("cpu_usage")),
            memory_total_mb=_parse_float(payload.get("memory_total_mb")),
            memory_available_mb=_parse_float(payload.get("memory_available_mb")),
            disk_total_mb=_parse_float(payload.get("disk_total_mb")),
            disk_used_mb=_parse_float(payload.get("disk_used_mb")),
            temperature_c=_parse_float(payload.get("temperature_c")),
            pluto_temp_c=_parse_float(payload.get("pluto_temp_c")),
            zynq_temp_c=_parse_float(payload.get("zynq_temp_c")),
            uptime_s=_parse_float(payload.get("uptime_s")),
            speed_mps=_parse_float(payload.get("speed_mps")),
            track_deg=_parse_float(payload.get("track_deg")),
            gps_fix=_parse_bool(payload.get("gps_fix"), default=False),
            time_source=_parse_str(payload.get("time_source")),
            gpsd_time_utc=_parse_str(payload.get("gpsd_time_utc")),
            updated=_parse_int(payload.get("updated")),
        )

    @classmethod
    def restore_placeholder(cls, kit_id: str) -> Kit:
        return cls(kit_id=kit_id, available=False)

    @property
    def has_position(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def with_availability(self, available: bool) -> Kit:
        return replace(self, available=available)

    def with_last_seen(self, last_seen: datetime) -> Kit:
        return replace(self, last_seen=last_seen)


@dataclass(slots=True, frozen=True)
class Drone:
    """A drone observed by one or more WarDragon kits."""

    drone_id: str
    track_type: str = "drone"
    description: str | None = None
    mac: str | None = None
    id_type: str | None = None
    caa_id: str | None = None

    latitude: float | None = None
    longitude: float | None = None
    alt: float | None = None
    height: float | None = None
    pressure_altitude: float | None = None
    height_type: str | None = None

    speed: float | None = None
    vspeed: float | None = None
    direction: float | None = None

    pilot_lat: float | None = None
    pilot_lon: float | None = None
    home_lat: float | None = None
    home_lon: float | None = None

    ua_type: int | None = None
    ua_type_name: str | None = None
    op_status: str | None = None
    ew_dir: str | None = None

    operator_id: str | None = None
    operator_id_type: str | None = None

    rid_make: str | None = None
    rid_model: str | None = None
    rid_status: str | None = None
    rid_tracking: str | None = None
    rid_source: str | None = None
    rid_lookup_attempted: bool = False
    rid_lookup_success: bool = False

    horizontal_accuracy: str | None = None
    vertical_accuracy: str | None = None
    baro_accuracy: str | None = None
    speed_accuracy: str | None = None
    timestamp_accuracy: str | None = None
    gps_accuracy: float | None = None

    timestamp: str | None = None
    rid_timestamp: str | None = None
    observed_at: float | None = None

    rssi: float | None = None
    freq: float | None = None
    freq_mhz: float | None = None
    transport: str | None = None

    seen_by: str | None = None

    rssi_by_kit: dict[str, float] = field(default_factory=dict)

    available: bool = True
    last_seen: datetime | None = None
    received_at: datetime | None = None

    @classmethod
    def from_drone_payload(cls, payload: dict[str, Any]) -> Drone | None:
        if not isinstance(payload, dict):
            _LOGGER.debug("Drone payload not a dict: %s", _truncate_payload_repr({"raw": payload}))
            return None
        drone_id = _parse_str(payload.get("id"))
        if drone_id is None:
            _LOGGER.debug("Drone payload missing id: %s", _truncate_payload_repr(payload))
            return None
        track_type = _parse_str(payload.get("track_type")) or "drone"
        if track_type != "drone":
            _LOGGER.debug("Drone payload track_type=%r not drone, dropping: %s", track_type, _truncate_payload_repr(payload))
            return None

        lat = _parse_float(payload.get("lat") if payload.get("lat") is not None else payload.get("latitude"))
        lon = _parse_float(payload.get("lon") if payload.get("lon") is not None else payload.get("longitude"))
        lat, lon = _filter_no_fix(lat, lon)

        pilot_lat, pilot_lon = _filter_no_fix(_parse_float(payload.get("pilot_lat")), _parse_float(payload.get("pilot_lon")))
        home_lat, home_lon = _filter_no_fix(_parse_float(payload.get("home_lat")), _parse_float(payload.get("home_lon")))

        seen_by = _parse_str(payload.get("seen_by"))
        rssi = _parse_float(payload.get("rssi"))
        rssi_by_kit: dict[str, float] = {}
        if seen_by is not None and rssi is not None:
            rssi_by_kit[seen_by] = rssi

        return cls(
            drone_id=drone_id,
            track_type=track_type,
            description=_parse_str(payload.get("description")),
            mac=_parse_str(payload.get("mac")),
            id_type=_parse_str(payload.get("id_type")),
            caa_id=_parse_str(payload.get("caa_id")),
            latitude=lat,
            longitude=lon,
            alt=_parse_float(payload.get("alt")),
            height=_parse_float(payload.get("height")),
            pressure_altitude=_parse_float(payload.get("pressure_altitude")),
            height_type=_parse_str(payload.get("height_type")),
            speed=_parse_float(payload.get("speed")),
            vspeed=_parse_float(payload.get("vspeed")),
            direction=_parse_float(payload.get("direction")),
            pilot_lat=pilot_lat,
            pilot_lon=pilot_lon,
            home_lat=home_lat,
            home_lon=home_lon,
            ua_type=_parse_int(payload.get("ua_type")),
            ua_type_name=_parse_str(payload.get("ua_type_name")),
            op_status=_parse_str(payload.get("op_status")),
            ew_dir=_parse_str(payload.get("ew_dir")),
            operator_id=_parse_str(payload.get("operator_id")),
            operator_id_type=_parse_str(payload.get("operator_id_type")),
            rid_make=_parse_str(payload.get("rid_make")),
            rid_model=_parse_str(payload.get("rid_model")),
            rid_status=_parse_str(payload.get("rid_status")),
            rid_tracking=_parse_str(payload.get("rid_tracking")),
            rid_source=_parse_str(payload.get("rid_source")),
            rid_lookup_attempted=_parse_bool(payload.get("rid_lookup_attempted"), default=False),
            rid_lookup_success=_parse_bool(payload.get("rid_lookup_success"), default=False),
            horizontal_accuracy=_parse_str(payload.get("horizontal_accuracy")),
            vertical_accuracy=_parse_str(payload.get("vertical_accuracy")),
            baro_accuracy=_parse_str(payload.get("baro_accuracy")),
            speed_accuracy=_parse_str(payload.get("speed_accuracy")),
            timestamp_accuracy=_parse_str(payload.get("timestamp_accuracy")),
            gps_accuracy=_parse_float(payload.get("gps_accuracy")),
            timestamp=_parse_str(payload.get("timestamp")),
            rid_timestamp=_parse_str(payload.get("rid_timestamp")),
            observed_at=_parse_float(payload.get("observed_at")),
            rssi=rssi,
            freq=_parse_float(payload.get("freq")),
            freq_mhz=_parse_float(payload.get("freq_mhz")),
            transport=_parse_str(payload.get("transport")),
            seen_by=seen_by,
            rssi_by_kit=rssi_by_kit,
        )

    @classmethod
    def restore_placeholder(cls, drone_id: str, last_seen: datetime | None = None) -> Drone:
        return cls(drone_id=drone_id, available=False, last_seen=last_seen)

    @property
    def has_position(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def has_pilot(self) -> bool:
        return self.pilot_lat is not None and self.pilot_lon is not None

    @property
    def has_home(self) -> bool:
        return self.home_lat is not None and self.home_lon is not None

    @property
    def protocol_family(self) -> str | None:
        """DroneID protocol family parsed from description.

        Returns `O2`, `O3`, `O4`, `OcuSync`, `WiFi-Beacon`, `WiFi-NaN`,
        `BT5-LR`, `ISM-FHSS`, or None when undeterminable. Inspects the
        `transport` field first (authoritative for non-DJI), then the
        `description` field for DJI O*/OcuSync markers.
        """
        if self.transport:
            t = self.transport.upper()
            if "WIFI-BEACON" in t or "WIFI_BEACON" in t:
                return "WiFi-Beacon"
            if "WIFI-NAN" in t or "WIFI_NAN" in t:
                return "WiFi-NaN"
            if "BT5" in t or "BLUETOOTH" in t:
                return "BT5-LR"
            if "ISM-FHSS" in t or "ISM_FHSS" in t:
                return "ISM-FHSS"
        if self.description:
            d = self.description.upper()
            if "(O4)" in d or " O4 " in d or d.endswith(" O4") or "DJI O4" in d:
                return "O4"
            if "(O3)" in d or " O3 " in d or d.endswith(" O3") or "DJI O3" in d:
                return "O3"
            if "(O2)" in d or " O2 " in d or d.endswith(" O2") or "DJI O2" in d:
                return "O2"
            if "OCUSYNC" in d:
                return "OcuSync"
        return None

    @property
    def freq_band(self) -> str | None:
        """Frequency band derived from `freq_mhz`. Returns `2.4GHz`, `5.2GHz`,
        `5.8GHz`, `900MHz`, or None if frequency is unknown / out of range."""
        f = self.freq_mhz
        if f is None:
            return None
        if 902 <= f <= 928:
            return "900MHz"
        if 2400 <= f <= 2500:
            return "2.4GHz"
        if 5150 <= f <= 5350:
            return "5.2GHz"
        if 5470 <= f <= 5895:
            return "5.8GHz"
        return None

    def merged_with(self, other: Drone) -> Drone:
        """Multi-kit fusion: merge `other` (newer payload) into this drone.

        Position comes from the kit reporting the strongest RSSI; per-kit RSSIs
        accumulate as `rssi_by_kit`. Non-position fields take the newer value
        when present, falling back to the previous value otherwise.
        """
        merged_rssi_by_kit = dict(self.rssi_by_kit)
        merged_rssi_by_kit.update(other.rssi_by_kit)

        best_kit = None
        best_rssi = None
        for kit, rssi in merged_rssi_by_kit.items():
            if best_rssi is None or rssi > best_rssi:
                best_kit = kit
                best_rssi = rssi

        use_other_position = (
            other.has_position
            and (other.seen_by == best_kit or not self.has_position)
        )

        def pick(new_val: Any, old_val: Any) -> Any:
            return new_val if new_val is not None else old_val

        return replace(
            other,
            description=pick(other.description, self.description),
            mac=pick(other.mac, self.mac),
            id_type=pick(other.id_type, self.id_type),
            caa_id=pick(other.caa_id, self.caa_id),
            latitude=other.latitude if use_other_position else self.latitude,
            longitude=other.longitude if use_other_position else self.longitude,
            alt=pick(other.alt, self.alt),
            height=pick(other.height, self.height),
            speed=pick(other.speed, self.speed),
            vspeed=pick(other.vspeed, self.vspeed),
            direction=pick(other.direction, self.direction),
            pilot_lat=pick(other.pilot_lat, self.pilot_lat),
            pilot_lon=pick(other.pilot_lon, self.pilot_lon),
            home_lat=pick(other.home_lat, self.home_lat),
            home_lon=pick(other.home_lon, self.home_lon),
            ua_type=pick(other.ua_type, self.ua_type),
            ua_type_name=pick(other.ua_type_name, self.ua_type_name),
            op_status=pick(other.op_status, self.op_status),
            ew_dir=pick(other.ew_dir, self.ew_dir),
            operator_id=pick(other.operator_id, self.operator_id),
            operator_id_type=pick(other.operator_id_type, self.operator_id_type),
            rid_make=pick(other.rid_make, self.rid_make),
            rid_model=pick(other.rid_model, self.rid_model),
            rid_status=pick(other.rid_status, self.rid_status),
            rid_tracking=pick(other.rid_tracking, self.rid_tracking),
            rid_source=pick(other.rid_source, self.rid_source),
            rid_lookup_attempted=other.rid_lookup_attempted or self.rid_lookup_attempted,
            rid_lookup_success=other.rid_lookup_success or self.rid_lookup_success,
            rssi=best_rssi if best_rssi is not None else pick(other.rssi, self.rssi),
            freq=pick(other.freq, self.freq),
            freq_mhz=pick(other.freq_mhz, self.freq_mhz),
            transport=pick(other.transport, self.transport),
            seen_by=best_kit or other.seen_by or self.seen_by,
            rssi_by_kit=merged_rssi_by_kit,
        )

    def with_availability(self, available: bool) -> Drone:
        return replace(self, available=available)

    def with_last_seen(self, last_seen: datetime, received_at: datetime | None = None) -> Drone:
        return replace(self, last_seen=last_seen, received_at=received_at or last_seen)


@dataclass(slots=True, frozen=True)
class Signal:
    """An FPV / RF signal detection from `wardragon/signals`."""

    uid: str
    signal_type: str | None = None
    source: str | None = None
    callsign: str | None = None
    description: str | None = None
    center_hz: float | None = None
    bandwidth_hz: float | None = None
    rssi: float | None = None
    pal: float | None = None
    ntsc: float | None = None
    sensor_lat: float | None = None
    sensor_lon: float | None = None
    sensor_alt: float | None = None
    lat: float | None = None
    lon: float | None = None
    alt: float | None = None
    radius_m: float | None = None
    seen_by: str | None = None
    observed_at: float | None = None

    last_seen: datetime | None = None
    received_at: datetime | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Signal | None:
        if not isinstance(payload, dict):
            return None
        uid = _parse_str(payload.get("uid"))
        if uid is None:
            return None
        lat = _parse_float(
            payload.get("lat") if payload.get("lat") is not None else payload.get("latitude")
        )
        lon = _parse_float(
            payload.get("lon") if payload.get("lon") is not None else payload.get("longitude")
        )
        lat, lon = _filter_no_fix(lat, lon)
        return cls(
            uid=uid,
            signal_type=_parse_str(payload.get("signal_type")),
            source=_parse_str(payload.get("source")),
            callsign=_parse_str(payload.get("callsign")),
            description=_parse_str(payload.get("description")),
            center_hz=_parse_float(payload.get("center_hz")),
            bandwidth_hz=_parse_float(payload.get("bandwidth_hz")),
            rssi=_parse_float(payload.get("rssi")),
            pal=_parse_float(payload.get("pal")),
            ntsc=_parse_float(payload.get("ntsc")),
            sensor_lat=_parse_float(payload.get("sensor_lat")),
            sensor_lon=_parse_float(payload.get("sensor_lon")),
            sensor_alt=_parse_float(payload.get("sensor_alt")),
            lat=lat,
            lon=lon,
            alt=_parse_float(payload.get("alt")),
            radius_m=_parse_float(payload.get("radius_m")),
            seen_by=_parse_str(payload.get("seen_by")),
            observed_at=_parse_float(payload.get("observed_at")),
        )

    @property
    def has_position(self) -> bool:
        return self.lat is not None and self.lon is not None

    @property
    def center_mhz(self) -> float | None:
        return self.center_hz / 1_000_000.0 if self.center_hz is not None else None

    @property
    def bandwidth_mhz(self) -> float | None:
        return self.bandwidth_hz / 1_000_000.0 if self.bandwidth_hz is not None else None

    def with_last_seen(self, last_seen: datetime, received_at: datetime | None = None) -> Signal:
        return replace(self, last_seen=last_seen, received_at=received_at or last_seen)
