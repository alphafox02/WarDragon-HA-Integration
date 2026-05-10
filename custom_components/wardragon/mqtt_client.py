"""MQTT subscriber for the WarDragon integration."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback

from .const import (
    MQTT_QOS,
    parse_service_topic,
    parse_system_topic,
    topic_drones_aggregate,
    topic_service_availability_wildcard,
    topic_signals_aggregate,
    topic_system_attrs_wildcard,
    topic_system_availability_wildcard,
)

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator

_LOGGER = logging.getLogger(__name__)


def _decode_text(payload: Any) -> str | None:
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError:
            return None
    if not isinstance(payload, str):
        return None
    return payload.strip() or None


def _decode_json_object(msg) -> dict[str, Any] | None:
    raw = _decode_text(msg.payload)
    if raw is None or raw == "None":
        return None
    try:
        decoded = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    return decoded if isinstance(decoded, dict) else None


def _decode_availability(msg) -> bool | None:
    raw = _decode_text(msg.payload)
    if raw is None:
        return None
    s = raw.lower()
    if s == "online":
        return True
    if s == "offline":
        return False
    return None


class WarDragonMQTTSubscriber:
    """Subscribe to wardragon/* topics and dispatch decoded payloads."""

    def __init__(self, hass: HomeAssistant, coordinator: WarDragonCoordinator, prefix: str) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.prefix = prefix
        self._unsub: list[Callable[[], None]] = []

    async def async_setup(self) -> None:
        topics: tuple[tuple[str, Callable], ...] = (
            (topic_drones_aggregate(self.prefix), self._on_drone_aggregate),
            (topic_system_attrs_wildcard(self.prefix), self._on_system_attrs),
            (topic_system_availability_wildcard(self.prefix), self._on_system_availability),
            (topic_service_availability_wildcard(self.prefix), self._on_service_availability),
            (topic_signals_aggregate(self.prefix), self._on_signal_aggregate),
        )
        for topic, handler in topics:
            unsub = await mqtt.async_subscribe(self.hass, topic, handler, qos=MQTT_QOS)
            self._unsub.append(unsub)
        _LOGGER.info("WarDragon subscribed to MQTT topics under %s/*", self.prefix)

    async def async_unload(self) -> None:
        while self._unsub:
            try:
                self._unsub.pop()()
            except Exception:
                _LOGGER.debug("MQTT unsubscribe failed", exc_info=True)

    @callback
    def _on_drone_aggregate(self, msg) -> None:
        payload = _decode_json_object(msg)
        if payload is None:
            return
        self.hass.async_create_task(
            self.coordinator.async_handle_drone_payload(payload, retained=bool(msg.retain))
        )

    @callback
    def _on_system_attrs(self, msg) -> None:
        parsed_topic = parse_system_topic(self.prefix, msg.topic)
        if parsed_topic is None or parsed_topic[1] != "attrs":
            return
        payload = _decode_json_object(msg)
        if payload is None:
            return
        self.hass.async_create_task(
            self.coordinator.async_handle_system_attrs(payload, retained=bool(msg.retain))
        )

    @callback
    def _on_system_availability(self, msg) -> None:
        parsed_topic = parse_system_topic(self.prefix, msg.topic)
        if parsed_topic is None or parsed_topic[1] != "availability":
            return
        kit_id = parsed_topic[0]
        online = _decode_availability(msg)
        if online is None:
            return
        self.hass.async_create_task(
            self.coordinator.async_handle_system_availability(kit_id, online)
        )

    @callback
    def _on_service_availability(self, msg) -> None:
        kit_id = parse_service_topic(self.prefix, msg.topic)
        if kit_id is None:
            return
        online = _decode_availability(msg)
        if online is None:
            return
        self.hass.async_create_task(
            self.coordinator.async_handle_service_availability(kit_id, online)
        )

    @callback
    def _on_signal_aggregate(self, msg) -> None:
        payload = _decode_json_object(msg)
        if payload is None:
            return
        self.hass.async_create_task(
            self.coordinator.async_handle_signal_payload(payload, retained=bool(msg.retain))
        )
