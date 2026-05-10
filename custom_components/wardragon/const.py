"""Constants for the WarDragon integration."""

from __future__ import annotations

import re

DOMAIN = "wardragon"
MANUFACTURER = "CEMAXECUTER"
MODEL = "WarDragon"
STORAGE_VERSION = 1

CONF_MQTT_PREFIX = "mqtt_prefix"
CONF_DRONE_INACTIVITY_TIMEOUT = "drone_inactivity_timeout"
CONF_DRONE_PURGE_AFTER = "drone_purge_after"
CONF_KIT_OFFLINE_TIMEOUT = "kit_offline_timeout"

DEFAULT_MQTT_PREFIX = "wardragon"
DEFAULT_DRONE_INACTIVITY_TIMEOUT = 300
DEFAULT_DRONE_PURGE_AFTER = 86400
DEFAULT_KIT_OFFLINE_TIMEOUT = 60

MQTT_PREFIX_RE = re.compile(r"^[a-zA-Z0-9_/-]+$")

MQTT_QOS = 1

NO_FIX_LAT = 0.0
NO_FIX_LON = 0.0

SIGNAL_NEW_KIT = f"{DOMAIN}_new_kit"
SIGNAL_NEW_DRONE = f"{DOMAIN}_new_drone"


def kit_update_signal(kit_id: str) -> str:
    return f"{DOMAIN}_kit_update_{kit_id}"


def drone_update_signal(drone_id: str) -> str:
    return f"{DOMAIN}_drone_update_{drone_id}"


EVENT_DRONE_DETECTED = "wardragon_drone_detected"
EVENT_DRONE_LOST = "wardragon_drone_lost"
EVENT_DRONE_PURGED = "wardragon_drone_purged"
EVENT_KIT_OFFLINE = "wardragon_kit_offline"
EVENT_SIGNAL_DETECTED = "wardragon_signal_detected"

SIGNAL_NEW_KIT_SIGNAL_CHANNEL = f"{DOMAIN}_new_kit_signal_channel"


def kit_signal_update_signal(kit_id: str) -> str:
    return f"{DOMAIN}_signal_update_{kit_id}"


def topic_drones_aggregate(prefix: str) -> str:
    return f"{prefix}/drones"


def topic_system_attrs_wildcard(prefix: str) -> str:
    return f"{prefix}/system/+/attrs"


def topic_system_availability_wildcard(prefix: str) -> str:
    return f"{prefix}/system/+/availability"


def topic_service_availability_wildcard(prefix: str) -> str:
    return f"{prefix}/service/+/availability"


def topic_signals_aggregate(prefix: str) -> str:
    return f"{prefix}/signals"


def parse_system_topic(prefix: str, topic: str) -> tuple[str, str] | None:
    """Extract (kit_id, suffix) from `<prefix>/system/<kit_id>/<suffix>`.

    Returns None for topics that don't match the expected shape.
    """
    head = f"{prefix}/system/"
    if not topic.startswith(head):
        return None
    rest = topic[len(head):]
    parts = rest.split("/", 1)
    if len(parts) != 2:
        return None
    kit_id, suffix = parts
    if not kit_id or not suffix:
        return None
    return kit_id, suffix


def parse_service_topic(prefix: str, topic: str) -> str | None:
    """Extract `kit_id` from `<prefix>/service/<kit_id>/availability`."""
    head = f"{prefix}/service/"
    tail = "/availability"
    if not topic.startswith(head) or not topic.endswith(tail):
        return None
    kit_id = topic[len(head): -len(tail)]
    return kit_id or None
