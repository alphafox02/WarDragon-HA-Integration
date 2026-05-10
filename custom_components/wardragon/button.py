"""Per-drone clear button."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_NEW_DRONE
from .entity import WarDragonDroneEntity

if TYPE_CHECKING:
    from .coordinator import WarDragonCoordinator

CLEAR_DRONE_DESC = ButtonEntityDescription(
    key="clear",
    translation_key="clear_drone",
    name="Clear drone",
    icon="mdi:delete-outline",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WarDragonCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    seen: set[str] = set()

    initial: list = []
    for drone in coordinator.get_all_drones():
        if drone.drone_id not in seen:
            seen.add(drone.drone_id)
            initial.append(WarDragonClearDroneButton(coordinator, drone.drone_id, CLEAR_DRONE_DESC))
    if initial:
        async_add_entities(initial)

    @callback
    def _on_new_drone(drone_id: str) -> None:
        if drone_id in seen:
            return
        seen.add(drone_id)
        async_add_entities([WarDragonClearDroneButton(coordinator, drone_id, CLEAR_DRONE_DESC)])

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_DRONE, _on_new_drone))


class WarDragonClearDroneButton(WarDragonDroneEntity, ButtonEntity):
    async def async_press(self) -> None:
        await self.coordinator.async_clear_drone(self.drone_id)
