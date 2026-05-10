"""Sensor platform for the WarDragon integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SIGNAL_NEW_DRONE,
    SIGNAL_NEW_KIT,
    SIGNAL_NEW_KIT_SIGNAL_CHANNEL,
)
from .entity import WarDragonDroneEntity, WarDragonKitEntity, WarDragonKitSignalEntity
from .sensor_definitions import (
    DRONE_SENSORS,
    KIT_SENSORS,
    SIGNAL_SENSORS,
    DroneSensorDescription,
    KitSensorDescription,
    SignalSensorDescription,
)

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WarDragonCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    seen_kits: set[str] = set()
    seen_drones: set[str] = set()
    seen_signal_channels: set[str] = set()

    initial: list = []
    for kit in coordinator.get_all_kits():
        if kit.kit_id in seen_kits:
            continue
        seen_kits.add(kit.kit_id)
        for desc in KIT_SENSORS:
            initial.append(WarDragonKitSensor(coordinator, kit.kit_id, desc))
    for drone in coordinator.get_all_drones():
        if drone.drone_id in seen_drones:
            continue
        seen_drones.add(drone.drone_id)
        for desc in DRONE_SENSORS:
            initial.append(WarDragonDroneSensor(coordinator, drone.drone_id, desc))
    for kit_id in coordinator.get_signal_channels():
        if kit_id in seen_signal_channels:
            continue
        seen_signal_channels.add(kit_id)
        for desc in SIGNAL_SENSORS:
            initial.append(WarDragonSignalSensor(coordinator, kit_id, desc))
    if initial:
        async_add_entities(initial)

    @callback
    def _on_new_kit(kit_id: str) -> None:
        if kit_id in seen_kits:
            return
        seen_kits.add(kit_id)
        async_add_entities(
            WarDragonKitSensor(coordinator, kit_id, desc) for desc in KIT_SENSORS
        )

    @callback
    def _on_new_drone(drone_id: str) -> None:
        if drone_id in seen_drones:
            return
        seen_drones.add(drone_id)
        async_add_entities(
            WarDragonDroneSensor(coordinator, drone_id, desc) for desc in DRONE_SENSORS
        )

    @callback
    def _on_new_signal_channel(kit_id: str) -> None:
        if kit_id in seen_signal_channels:
            return
        seen_signal_channels.add(kit_id)
        async_add_entities(
            WarDragonSignalSensor(coordinator, kit_id, desc) for desc in SIGNAL_SENSORS
        )

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_KIT, _on_new_kit))
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_DRONE, _on_new_drone))
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_NEW_KIT_SIGNAL_CHANNEL, _on_new_signal_channel)
    )


class WarDragonKitSensor(WarDragonKitEntity, SensorEntity):
    entity_description: KitSensorDescription

    @property
    def native_value(self):
        kit = self.kit
        if kit is None:
            return None
        try:
            return self.entity_description.value_fn(kit)
        except Exception:  # pragma: no cover
            return None


class WarDragonDroneSensor(WarDragonDroneEntity, SensorEntity):
    entity_description: DroneSensorDescription

    @property
    def native_value(self):
        drone = self.drone
        if drone is None:
            return None
        try:
            return self.entity_description.value_fn(drone)
        except Exception:  # pragma: no cover
            return None


class WarDragonSignalSensor(WarDragonKitSignalEntity, SensorEntity):
    entity_description: SignalSensorDescription

    @property
    def native_value(self):
        signal = self.signal
        if signal is None:
            return None
        try:
            return self.entity_description.value_fn(signal)
        except Exception:  # pragma: no cover
            return None
