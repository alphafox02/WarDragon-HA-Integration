"""Binary sensors for WarDragon kits and drones."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_NEW_DRONE, SIGNAL_NEW_KIT
from .entity import WarDragonDroneEntity, WarDragonKitEntity

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator
    from .models import Drone, Kit


@dataclass(frozen=True, kw_only=True)
class KitBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[Kit], bool | None] = lambda _k: None


@dataclass(frozen=True, kw_only=True)
class DroneBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[Drone], bool | None] = lambda _d: None


KIT_BINARY_SENSORS: tuple[KitBinarySensorDescription, ...] = (
    KitBinarySensorDescription(
        key="gps_fix",
        translation_key="gps_fix",
        name="GPS fix",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:crosshairs-gps",
        value_fn=lambda k: k.gps_fix,
    ),
    KitBinarySensorDescription(
        key="online",
        translation_key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda k: k.available,
    ),
)


DRONE_BINARY_SENSORS: tuple[DroneBinarySensorDescription, ...] = (
    DroneBinarySensorDescription(
        key="online",
        translation_key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda d: d.available,
    ),
    DroneBinarySensorDescription(
        key="rid_lookup_success",
        translation_key="rid_lookup_success",
        name="RID lookup matched",
        icon="mdi:database-check",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.rid_lookup_success if d.rid_lookup_attempted else None,
    ),
    DroneBinarySensorDescription(
        key="has_pilot",
        translation_key="has_pilot",
        name="Pilot location known",
        icon="mdi:account-star",
        value_fn=lambda d: d.has_pilot,
    ),
    DroneBinarySensorDescription(
        key="has_home",
        translation_key="has_home",
        name="Home location known",
        icon="mdi:home-map-marker",
        value_fn=lambda d: d.has_home,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WarDragonCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    seen_kits: set[str] = set()
    seen_drones: set[str] = set()

    initial: list = []
    for kit in coordinator.get_all_kits():
        if kit.kit_id in seen_kits:
            continue
        seen_kits.add(kit.kit_id)
        for desc in KIT_BINARY_SENSORS:
            initial.append(WarDragonKitBinarySensor(coordinator, kit.kit_id, desc))
    for drone in coordinator.get_all_drones():
        if drone.drone_id in seen_drones:
            continue
        seen_drones.add(drone.drone_id)
        for desc in DRONE_BINARY_SENSORS:
            initial.append(WarDragonDroneBinarySensor(coordinator, drone.drone_id, desc))
    if initial:
        async_add_entities(initial)

    @callback
    def _on_new_kit(kit_id: str) -> None:
        if kit_id in seen_kits:
            return
        seen_kits.add(kit_id)
        async_add_entities(
            WarDragonKitBinarySensor(coordinator, kit_id, desc) for desc in KIT_BINARY_SENSORS
        )

    @callback
    def _on_new_drone(drone_id: str) -> None:
        if drone_id in seen_drones:
            return
        seen_drones.add(drone_id)
        async_add_entities(
            WarDragonDroneBinarySensor(coordinator, drone_id, desc) for desc in DRONE_BINARY_SENSORS
        )

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_KIT, _on_new_kit))
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_DRONE, _on_new_drone))


class WarDragonKitBinarySensor(WarDragonKitEntity, BinarySensorEntity):
    entity_description: KitBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        kit = self.kit
        if kit is None:
            return None
        return self.entity_description.value_fn(kit)


class WarDragonDroneBinarySensor(WarDragonDroneEntity, BinarySensorEntity):
    entity_description: DroneBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        drone = self.drone
        if drone is None:
            return None
        return self.entity_description.value_fn(drone)
