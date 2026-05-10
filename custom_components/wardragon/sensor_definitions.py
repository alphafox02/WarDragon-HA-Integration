"""Sensor entity descriptions for WarDragon kits and drones."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfFrequency,
    UnitOfInformation,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory

if TYPE_CHECKING:
    from .models import Drone, Kit, Signal

DBM = "dBm"
DEGREES = "°"


@dataclass(frozen=True, kw_only=True)
class KitSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Kit], Any] = lambda _k: None


@dataclass(frozen=True, kw_only=True)
class DroneSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Drone], Any] = lambda _d: None


@dataclass(frozen=True, kw_only=True)
class SignalSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Signal], Any] = lambda _s: None


KIT_SENSORS: tuple[KitSensorDescription, ...] = (
    KitSensorDescription(
        key="cpu_usage",
        translation_key="cpu_usage",
        name="CPU usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cpu-64-bit",
        value_fn=lambda k: k.cpu_usage,
    ),
    KitSensorDescription(
        key="memory_available_mb",
        translation_key="memory_available_mb",
        name="Memory available",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda k: k.memory_available_mb,
    ),
    KitSensorDescription(
        key="memory_total_mb",
        translation_key="memory_total_mb",
        name="Memory total",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:memory",
        value_fn=lambda k: k.memory_total_mb,
    ),
    KitSensorDescription(
        key="disk_used_mb",
        translation_key="disk_used_mb",
        name="Disk used",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:harddisk",
        value_fn=lambda k: k.disk_used_mb,
    ),
    KitSensorDescription(
        key="disk_total_mb",
        translation_key="disk_total_mb",
        name="Disk total",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:harddisk",
        value_fn=lambda k: k.disk_total_mb,
    ),
    KitSensorDescription(
        key="temperature_c",
        translation_key="temperature_c",
        name="Mainboard temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda k: k.temperature_c,
    ),
    KitSensorDescription(
        key="pluto_temp_c",
        translation_key="pluto_temp_c",
        name="PlutoSDR temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda k: k.pluto_temp_c,
    ),
    KitSensorDescription(
        key="zynq_temp_c",
        translation_key="zynq_temp_c",
        name="Zynq SoC temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda k: k.zynq_temp_c,
    ),
    KitSensorDescription(
        key="uptime_s",
        translation_key="uptime_s",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-outline",
        value_fn=lambda k: k.uptime_s,
    ),
    KitSensorDescription(
        key="hae",
        translation_key="hae",
        name="Altitude (HAE)",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda k: k.hae,
    ),
    KitSensorDescription(
        key="speed_mps",
        translation_key="speed_mps",
        name="Speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda k: k.speed_mps,
    ),
    KitSensorDescription(
        key="track_deg",
        translation_key="track_deg",
        name="Course",
        native_unit_of_measurement=DEGREES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:compass",
        value_fn=lambda k: k.track_deg,
    ),
    KitSensorDescription(
        key="time_source",
        translation_key="time_source",
        name="Time source",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:clock-outline",
        value_fn=lambda k: k.time_source,
    ),
)


DRONE_SENSORS: tuple[DroneSensorDescription, ...] = (
    DroneSensorDescription(
        key="rssi",
        translation_key="rssi",
        name="RSSI",
        native_unit_of_measurement=DBM,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.rssi,
    ),
    DroneSensorDescription(
        key="altitude",
        translation_key="altitude",
        name="Altitude",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:altimeter",
        value_fn=lambda d: d.alt,
    ),
    DroneSensorDescription(
        key="height",
        translation_key="height",
        name="Height",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:arrow-expand-vertical",
        value_fn=lambda d: d.height,
    ),
    DroneSensorDescription(
        key="speed",
        translation_key="speed",
        name="Speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.speed,
    ),
    DroneSensorDescription(
        key="vspeed",
        translation_key="vspeed",
        name="Vertical speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:axis-z-arrow",
        value_fn=lambda d: d.vspeed,
    ),
    DroneSensorDescription(
        key="direction",
        translation_key="direction",
        name="Heading",
        native_unit_of_measurement=DEGREES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:compass-outline",
        value_fn=lambda d: d.direction,
    ),
    DroneSensorDescription(
        key="freq_mhz",
        translation_key="freq_mhz",
        name="Frequency",
        native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.freq_mhz,
    ),
    DroneSensorDescription(
        key="freq_band",
        translation_key="freq_band",
        name="Frequency band",
        icon="mdi:radio-tower",
        value_fn=lambda d: d.freq_band,
    ),
    DroneSensorDescription(
        key="protocol_family",
        translation_key="protocol_family",
        name="Protocol family",
        icon="mdi:antenna",
        value_fn=lambda d: d.protocol_family,
    ),
    DroneSensorDescription(
        key="transport",
        translation_key="transport",
        name="Transport",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:antenna",
        value_fn=lambda d: d.transport,
    ),
    DroneSensorDescription(
        key="description",
        translation_key="description",
        name="Description",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:text-short",
        value_fn=lambda d: d.description,
    ),
    DroneSensorDescription(
        key="id_type",
        translation_key="id_type",
        name="ID type",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:identifier",
        value_fn=lambda d: d.id_type,
    ),
    DroneSensorDescription(
        key="ua_type_name",
        translation_key="ua_type_name",
        name="UA type",
        icon="mdi:drone",
        value_fn=lambda d: d.ua_type_name,
    ),
    DroneSensorDescription(
        key="caa_id",
        translation_key="caa_id",
        name="CAA registration",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:airport",
        value_fn=lambda d: d.caa_id,
    ),
    DroneSensorDescription(
        key="operator_id",
        translation_key="operator_id",
        name="Operator ID",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:account",
        value_fn=lambda d: d.operator_id,
    ),
    DroneSensorDescription(
        key="mac",
        translation_key="mac",
        name="MAC address",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:network-pos",
        value_fn=lambda d: d.mac,
    ),
    DroneSensorDescription(
        key="seen_by",
        translation_key="seen_by",
        name="Seen by",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:eye-outline",
        value_fn=lambda d: d.seen_by,
    ),
    DroneSensorDescription(
        key="kit_count",
        translation_key="kit_count",
        name="Observing kits",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        value_fn=lambda d: len(d.rssi_by_kit) if d.rssi_by_kit else None,
    ),
    DroneSensorDescription(
        key="rid_make",
        translation_key="rid_make",
        name="Manufacturer (RID lookup)",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:factory",
        value_fn=lambda d: d.rid_make,
    ),
    DroneSensorDescription(
        key="rid_model",
        translation_key="rid_model",
        name="Model (RID lookup)",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:tag-outline",
        value_fn=lambda d: d.rid_model,
    ),
    DroneSensorDescription(
        key="rid_status",
        translation_key="rid_status",
        name="Registration status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:check-decagram",
        value_fn=lambda d: d.rid_status,
    ),
    DroneSensorDescription(
        key="horizontal_accuracy",
        translation_key="horizontal_accuracy",
        name="Horizontal accuracy",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:crosshairs-gps",
        value_fn=lambda d: d.horizontal_accuracy,
    ),
)


SIGNAL_SENSORS: tuple[SignalSensorDescription, ...] = (
    SignalSensorDescription(
        key="type",
        translation_key="signal_type",
        name="Signal type",
        icon="mdi:waveform",
        value_fn=lambda s: s.signal_type,
    ),
    SignalSensorDescription(
        key="source",
        translation_key="signal_source",
        name="Signal source",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:radio-handheld",
        value_fn=lambda s: s.source,
    ),
    SignalSensorDescription(
        key="callsign",
        translation_key="signal_callsign",
        name="Signal callsign",
        icon="mdi:tag",
        value_fn=lambda s: s.callsign,
    ),
    SignalSensorDescription(
        key="rssi",
        translation_key="signal_rssi",
        name="Signal RSSI",
        native_unit_of_measurement=DBM,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.rssi,
    ),
    SignalSensorDescription(
        key="center_mhz",
        translation_key="signal_center_mhz",
        name="Signal centre frequency",
        native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.center_mhz,
    ),
    SignalSensorDescription(
        key="bandwidth_mhz",
        translation_key="signal_bandwidth_mhz",
        name="Signal bandwidth",
        native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.bandwidth_mhz,
    ),
    SignalSensorDescription(
        key="description",
        translation_key="signal_description",
        name="Signal description",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:text-short",
        value_fn=lambda s: s.description,
    ),
)
