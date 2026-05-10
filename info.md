# WarDragon for Home Assistant

A native Home Assistant integration for [WarDragon](https://github.com/alphafox02/WarDragon) drone detection kits.

## What you get

- Each detected drone created automatically as a Home Assistant **device** with a real-time **map** marker
- Full Remote ID telemetry: position, altitude, speed, heading, RSSI, operator, frequency band
- **DroneID protocol family** sensor (DJI O2/O3/O4, OcuSync, Wi-Fi NaN, BT5-LR) — surface what your kit is actually seeing
- **Multi-kit fusion** — when several WarDragon kits see the same drone, they fuse into one HA device with per-kit RSSIs as attributes, position taken from the kit with the strongest signal
- Kit health: CPU, memory, GPS, SDR temperatures, uptime, disk usage
- Pilot and home device_trackers (for DJI OcuSync detections)
- Native geofencing via Home Assistant **zones**
- **Custom services**: `wardragon.clear_drone`, `wardragon.export_drones`
- Ready-to-import automation blueprints: drone in zone, drone lost, kit offline, FPV/RF signal detected
- **HA diagnostics** download for support
- **Repair issues** that surface DragonSync misconfigurations

## Requirements

- Home Assistant 2024.1 or newer
- An MQTT broker reachable by both Home Assistant and DragonSync
- DragonSync v2.0 or newer running on your WarDragon kit, with `mqtt_ha_native_mode = true` in `config.ini` so DragonSync stops publishing its own HA discovery messages
