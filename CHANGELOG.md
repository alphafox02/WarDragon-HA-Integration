# Changelog

All notable changes to the WarDragon HA Integration are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

## [0.2.0] — 2026-05-09

Initial public release. Targets DragonSync v2.0+ kit-scoped MQTT topic schema.

### Added — Drone surface

- Drone `device_tracker` with HA map placement; `(0.0, 0.0)` no-fix sentinel filtered.
- Drone telemetry sensors: `rssi`, `altitude`, `height`, `speed`, `vspeed`, `direction`, `freq_mhz`, `transport`, `description`, `id_type`, `ua_type_name`, `caa_id`, `operator_id`, `mac`, `seen_by`, `horizontal_accuracy`.
- **DroneID protocol family** sensor — derives `O2`, `O3`, `O4`, `OcuSync`, `WiFi-Beacon`, `WiFi-NaN`, `BT5-LR`, `ISM-FHSS` from DragonSync's `description` and `transport` fields.
- **Frequency band** sensor — categorises drones into `900MHz`, `2.4GHz`, `5.2GHz`, `5.8GHz`.
- **FAA RID lookup** display: `rid_make`, `rid_model`, `rid_status` sensors plus `rid_lookup_success` binary sensor.
- **Pilot** and **home** device_trackers (active when DJI OcuSync detections include those points).
- Drone **online**, **has_pilot**, **has_home** binary sensors.
- **Multi-kit fusion**: drones seen by multiple kits fuse into one HA device with per-kit RSSIs as `rssi_by_kit` attribute and `Observing kits` count sensor; position taken from the kit reporting the strongest signal.
- Per-drone **Clear** button to remove a tracked drone from HA immediately.

### Added — Kit surface

- Kit `device_tracker` (gates on `gps_fix` and valid coordinates).
- Kit telemetry sensors: `cpu_usage`, memory available/total, disk used/total, mainboard temperature, **PlutoSDR temperature**, **Zynq SoC temperature**, uptime, GPS HAE, speed, course, time source.
- Kit **GPS fix** and **online** binary sensors.

### Added — Signals (FPV / RF detections)

- Per-kit signal channel: subscribes to `wardragon/signals` aggregate topic and surfaces the latest detection that kit observed.
- Signal sensors per kit: `signal_type`, `signal_source`, `signal_callsign`, `signal_rssi`, `signal_centre_mhz`, `signal_bandwidth_mhz`, `signal_description`.
- Signal `device_tracker` per kit (current detection location with `radius_m` accuracy).
- HA event `wardragon_signal_detected` fires for every signal (full payload as event data).

### Added — WarDragon COP (Common Operating Picture)

A bundled custom Lovelace card that ships with the integration. Auto-registers with Home Assistant on first install — drop it onto any dashboard via the card picker; no manual Lovelace resource line needed.

The COP card surfaces in one card:

- **Header stats**: active tracks, online kits, signals in the last hour.
- **Search bar**: live-filter drones by ID, description, operator ID, CAA registration, or seen-by kit.
- **Filter chips**: protocol family (`O2`, `O3`, `O4`, `OcuSync`, `WiFi-Beacon`, `WiFi-NaN`, `BT5-LR`, `ISM-FHSS`) and frequency band (`900MHz`, `2.4GHz`, `5.2GHz`, `5.8GHz`), plus an "online only" toggle.
- **Sort dropdown**: last-seen, RSSI (strongest first), altitude, speed, callsign.
- **Drone roster**: each tracked drone as a tile with status indicator, callsign, protocol family + band tags, RSSI / altitude / speed, observing-kit count, age, seen-by kit, info button (opens HA's more-info dialog), and clear button (calls `wardragon.clear_drone`).
- **Kit panel**: per-kit health card with online state, GPS fix, CPU, mainboard / Pluto / Zynq temperatures, uptime.
- **Recent signals feed**: latest FPV/RF detection per kit with type, callsign, centre frequency, bandwidth, source, age, RSSI.

Tactical layout for live counter-drone monitoring: dense info, dark-friendly, theme-aware via HA CSS variables, monospace values, subdued accent palette mirroring the WarDragon dragon mark.

### Added — Lifecycle

- Drone inactivity timeout (default 5 min): drone tracker marked unavailable, `wardragon_drone_lost` event fires.
- Drone purge after (default 24 h): drone removed from the device registry, `wardragon_drone_purged` event fires.
- Kit offline timeout (default 60 s): kit binary sensor flips, `wardragon_kit_offline` event fires.
- All three timeouts tunable in **Configure → Options** on the integration card.
- State persists across HA restarts (drone IDs and last-seen survive reboots).

### Added — Services

- `wardragon.clear_drone` — remove a tracked drone from HA immediately.
- `wardragon.export_drones` — return a JSON snapshot of every currently tracked drone, including multi-kit fusion attributes.

### Added — Bus events

- `wardragon_drone_detected`, `wardragon_drone_lost`, `wardragon_drone_purged`, `wardragon_kit_offline`, `wardragon_signal_detected` — listen for these in any automation.

### Added — Blueprints

- `notify_drone_in_zone`, `notify_drone_lost`, `notify_kit_offline`, `notify_signal_detected` (with optional `signal_type` and minimum-RSSI filters).

### Added — Operator UX

- HA **diagnostics** download with operator IDs, MACs, CAA IDs, and kit-ID hashes redacted.
- HA **repair issues** for "MQTT not loaded".
- Options flow for lifecycle timeout tuning.
- English translations for all entities, services, options, repair issues, and config flow strings.

### Architecture

- `manifest.json` `integration_type = "hub"` so one config entry can own multi-kit fusion devices.
- `iot_class = "local_push"` — pure MQTT subscription, no polling, no cloud.
- Config flow asks only for the MQTT topic prefix; relies on the standard HA MQTT integration for broker/credentials.
- Wildcard subscriptions on kit-scoped topics (`wardragon/system/+/attrs`, `wardragon/system/+/availability`, `wardragon/service/+/availability`) — multi-kit deployments work correctly out of the gate.
- COP card pipeline: TypeScript + Lit + Rollup, built in CI on tag push as an IIFE bundle, registered via `frontend.py` with explicit `customElements.define` for global-registry compatibility.

### Requirements

- Home Assistant 2024.1 or newer.
- DragonSync v2.0 or newer running on each WarDragon kit.
- DragonSync's `mqtt_ha_native_mode = true` to suppress its own `homeassistant/*` discovery configs.

### Operator dashboard recipe

A copy-paste sections-view dashboard YAML (COP on the left, native HA map on the right) lives in the README install section.
