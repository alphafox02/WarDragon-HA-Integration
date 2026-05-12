"""Base entity classes for WarDragon kits and drones."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityDescription

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    drone_update_signal,
    kit_signal_update_signal,
    kit_update_signal,
)

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator
    from .models import Drone, Kit, Signal


def kit_device_name(kit_id: str) -> str:
    # Full kit_id (e.g. "wardragon-BN95H4CG01058"). HA's device list shows
    # the full string; operators identify kits by their complete serial
    # rather than the last-N-chars tail.
    return kit_id


def drone_device_name(drone: Drone | None, drone_id: str) -> str:
    if drone is not None and drone.description:
        return drone.description
    # Full drone_id (e.g. "drone-2051FEABPT0000000207"). Operators identify
    # drones by their full Remote ID serial — matches what ATAK shows on
    # the track callsign and what FAA RID lookups key on.
    return drone_id


def drone_manufacturer(drone: Drone | None) -> str:
    if drone is not None:
        if drone.rid_make:
            return drone.rid_make
        if drone.description and drone.description.upper().startswith("DJI"):
            return "DJI"
    return "Unknown"


def drone_model(drone: Drone | None) -> str | None:
    if drone is None:
        return None
    if drone.rid_model:
        return drone.rid_model
    if drone.ua_type_name:
        return drone.ua_type_name
    return drone.description


class WarDragonKitEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: WarDragonCoordinator,
        kit_id: str,
        description: EntityDescription,
    ) -> None:
        self.coordinator = coordinator
        self.kit_id = kit_id
        self.entity_description = description
        self._attr_unique_id = f"{kit_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"kit:{kit_id}")},
            name=kit_device_name(kit_id),
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, kit_update_signal(self.kit_id), self.async_write_ha_state
            )
        )

    @property
    def kit(self) -> Kit | None:
        return self.coordinator.get_kit(self.kit_id)

    @property
    def available(self) -> bool:
        kit = self.kit
        return kit is not None and kit.available


class WarDragonKitSignalEntity(Entity):
    """An entity attached to a kit device but driven by signal-channel updates.

    Used for the kit's "current signal" sensors and tracker — what FPV/RF
    signal that kit is currently observing on `wardragon/signals`.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: WarDragonCoordinator,
        kit_id: str,
        description: EntityDescription,
    ) -> None:
        self.coordinator = coordinator
        self.kit_id = kit_id
        self.entity_description = description
        self._attr_unique_id = f"{kit_id}_signal_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"kit:{kit_id}")},
            name=kit_device_name(kit_id),
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, kit_signal_update_signal(self.kit_id), self.async_write_ha_state
            )
        )

    @property
    def signal(self) -> Signal | None:
        return self.coordinator.get_kit_signal(self.kit_id)

    @property
    def available(self) -> bool:
        return self.signal is not None


class WarDragonDroneEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: WarDragonCoordinator,
        drone_id: str,
        description: EntityDescription,
    ) -> None:
        self.coordinator = coordinator
        self.drone_id = drone_id
        self.entity_description = description
        self._attr_unique_id = f"{drone_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        # Live: name/manufacturer/model reflect the latest drone state so
        # FAA RID lookup results and BLE→DJI promotions surface in HA's
        # device registry without needing a re-register.
        drone = self.coordinator.get_drone(self.drone_id)
        return DeviceInfo(
            identifiers={(DOMAIN, f"drone:{self.drone_id}")},
            name=drone_device_name(drone, self.drone_id),
            manufacturer=drone_manufacturer(drone),
            model=drone_model(drone),
            serial_number=self.drone_id,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, drone_update_signal(self.drone_id), self.async_write_ha_state
            )
        )
        # Note: per-entity removal is NOT subscribed here. The coordinator
        # purges the drone's device from the device registry on inactivity;
        # HA cascades entity teardown automatically. Avoiding the redundant
        # path prevents double-remove warnings under load.

    @property
    def drone(self) -> Drone | None:
        return self.coordinator.get_drone(self.drone_id)

    @property
    def available(self) -> bool:
        drone = self.drone
        return drone is not None and drone.available
