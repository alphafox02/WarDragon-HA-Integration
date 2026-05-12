# WarDragon for Home Assistant

[![Validate](https://github.com/alphafox02/WarDragon-HA-Integration/actions/workflows/validate.yml/badge.svg)](https://github.com/alphafox02/WarDragon-HA-Integration/actions/workflows/validate.yml)
[![Tests](https://github.com/alphafox02/WarDragon-HA-Integration/actions/workflows/test.yml/badge.svg)](https://github.com/alphafox02/WarDragon-HA-Integration/actions/workflows/test.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration for the [WarDragon](https://github.com/alphafox02/WarDragon) drone-detection platform. Pulls live tracks, kit telemetry, and FPV/RF signal detections out of [DragonSync's](https://github.com/alphafox02/DragonSync) MQTT stream and turns them into Home Assistant **devices, sensors, trackers, services, blueprints, automation events, and a bundled tactical Lovelace card** — the **WarDragon Common Operating Picture (COP)**.

---

## What you get

### Devices

- **One device per detected drone**, populated with description, manufacturer, model, and serial from Remote ID + DJI metadata.
- **One device per WarDragon kit**, with full kit telemetry (CPU, memory, GPS, mainboard / PlutoSDR / Zynq SoC temperatures, uptime, disk).

### Live tracking

- Drone, **pilot**, and **home** positions on Home Assistant's map (separate `device_tracker` entities each).
- Kit GPS position on the map.
- Per-kit current FPV/RF signal source position (when detected).
- Multi-kit fusion: when two kits see the same drone, they fuse into a single device, position taken from the kit reporting the strongest signal, per-kit RSSIs preserved as `rssi_by_kit`.

### Telemetry sensors per drone

- RSSI, altitude, height, speed, vertical speed, heading.
- Frequency, transport, MAC, ID type, UA type, CAA registration, operator ID.
- **DroneID protocol family** — `O2` / `O3` / `O4` / `OcuSync` / `WiFi-Beacon` / `WiFi-NaN` / `BT5-LR` / `ISM-FHSS` parsed from `description` and `transport`.
- **Frequency band** — `900MHz` / `2.4GHz` / `5.2GHz` / `5.8GHz` derived from `freq_mhz`.
- **Observing kits** — count of kits currently seeing this drone.
- **FAA RID lookup display** — `rid_make`, `rid_model`, `rid_status` from DragonSync's lookup pipeline.

### Telemetry sensors per kit

- CPU usage, memory available / total, disk used / total.
- Mainboard temperature, **PlutoSDR temperature**, **Zynq SoC temperature**.
- Uptime, GPS HAE, kit ground speed and course, time source.
- Live FPV / RF signal channel: type, source, callsign, RSSI, centre frequency, bandwidth, position.

### Binary sensors

- Drone: online, RID lookup matched, has-pilot, has-home.
- Kit: online, GPS fix.

### Bundled tactical Lovelace card — WarDragon COP

The integration ships with a **Common Operating Picture (COP)** custom card that auto-registers with Home Assistant on first install. Drop it onto any dashboard via the card picker — no manual resource setup, no separate repository to install.

The COP gives you, in one card:

- **Header stat tiles** — active drones, kits online, signals in the last hour.
- **Drone list** — each detected drone as a tile with description, RSSI, protocol family, frequency band, observing-kit count, online indicator, and a one-click "clear" action.
- **Kit health glance** — per-kit CPU, temperatures, uptime, GPS state.
- **Recent signal feed** — the latest FPV/RF detection per kit, with type, callsign, frequency, bandwidth, RSSI.

Everything is theme-aware, dark-mode-friendly, and styled in a tactical layout suited to live counter-drone monitoring.

> Home Assistant's built-in **Map** view also works out of the box — every WarDragon `device_tracker` entity (drones, pilots, homes, kits, signal sources) drops onto it automatically. The COP card is what you use when you want a single-pane operator console; the HA map is what you use for general situational awareness.

### Custom services

- **`wardragon.clear_drone`** — remove a tracked drone from HA immediately. Useful for clearing stale tracks or curating the COP.
- **`wardragon.export_drones`** — return a JSON snapshot of every currently tracked drone, including all fusion attributes. Use as a service-with-response in scripts and exports.

### Automation events

Listen for these in any automation:

- `wardragon_drone_detected` — new drone first observed (data: `drone_id`, `seen_by`).
- `wardragon_drone_lost` — drone gone silent past inactivity timeout.
- `wardragon_drone_purged` — drone removed from device registry past purge timeout.
- `wardragon_kit_offline` — kit heartbeat or DragonSync LWT offline.
- `wardragon_signal_detected` — FPV/RF signal detection (full payload as event data).

### Automation blueprints (4)

Drop-in blueprints under **Settings → Automations & Scenes → Blueprints**:

- `notify_drone_in_zone` — fire when a drone enters a HA zone.
- `notify_drone_lost` — fire when a drone goes silent.
- `notify_kit_offline` — fire when a kit stops sending telemetry.
- `notify_signal_detected` — fire on FPV/RF signal detection, with optional `signal_type` and minimum-RSSI filters.

### Lifecycle

- **Drone inactivity timeout** (default 5 min) marks the drone unavailable.
- **Drone purge after** (default 24 h) removes the drone's device from HA.
- **Kit offline timeout** (default 60 s) flips the kit's online binary sensor.
- All three timeouts tunable in **Configure → Options** on the integration card.
- State persists across HA restarts (drone IDs and last-seen survive reboots).

### Operator UX

- **Diagnostics download** (Settings → Devices & Services → WarDragon → ⋮ → Download diagnostics) with operator IDs, MACs, CAA IDs, and kit-ID hashes redacted.
- **Repair issues** that surface common DragonSync misconfigurations.
- **Options flow** for lifecycle tuning.
- Full English translations for entities, services, options, repair issues, and config flow.

---

## Requirements

- **Home Assistant 2024.1** or newer.
- The HA **MQTT integration** loaded and connected to a broker.
- **DragonSync v2.0** or newer running on each WarDragon kit (kit-scoped MQTT topic schema).
- DragonSync's `mqtt_ha_enabled = false` in `config.ini` (this is the default, so most operators don't have to change anything). When `mqtt_ha_enabled` is `true`, DragonSync publishes its own `homeassistant/*` MQTT discovery configs in addition to whatever this integration creates, which produces duplicate entities. Either keep DragonSync's HA discovery off (recommended) or accept the duplicates.

---

## Installation

Full end-to-end walkthrough for a fresh Home Assistant install — including the HACS card install for `auto-entities` and the side-by-side dashboard YAML — lives in **[docs/INSTALL.md](docs/INSTALL.md)**. Follow that if you're new to this integration or starting from scratch.

For experienced operators, the short version:

### HACS (recommended)

1. HACS -> three-dot menu -> **Custom repositories** -> add `https://github.com/alphafox02/WarDragon-HA-Integration`, category **Integration**.
2. Install **WarDragon** from the HACS card.
3. Restart Home Assistant.
4. **Settings -> Devices & Services -> Add Integration** -> search **WarDragon**.
5. Accept default MQTT topic prefix `wardragon` (or override if your DragonSync uses something different).
6. The COP card auto-registers on first install — drop it onto any dashboard via the card picker.

For the **side-by-side COP + auto-discovering map** dashboard the project ships as its reference layout, see [docs/INSTALL.md](docs/INSTALL.md) section 5 onward. It walks through installing `auto-entities` from HACS and pasting the dashboard YAML.

For **alternative dashboard layouts** (tabbed, panel/wallboard, per-drone follow), see [docs/DASHBOARDS.md](docs/DASHBOARDS.md).

### Manual

1. **Install from a release, not from `main`.** The COP card bundle (`frontend/dist/wardragon-cop-card.js`) is gitignored — it's only built when a tagged release runs through CI. Grab `wardragon.zip` from the [Releases page](https://github.com/alphafox02/WarDragon-HA-Integration/releases) and extract `wardragon/` into your HA `config/custom_components/`.

   Or if you really want to install from `main`: `cd custom_components/wardragon/frontend && npm ci && npm run build` first to produce the bundle, then copy.
2. Restart Home Assistant.
3. Add the integration as above.

---

## Usage tips

- The first kit telemetry can take up to ~30 seconds on a freshly-imaged WarDragon to arrive — DragonSync defers system topics until its kit identity resolves. The kit device only appears in HA after that first message.
- Drones become unavailable after 5 minutes of silence and are purged after 24 hours by default. Both timeouts are tunable in **Configure → Options** on the integration card.
- Multi-kit operators: if a drone is `seen_by` an unexpected kit, check `rssi_by_kit` in the drone tracker's attributes — the integration takes position from the kit with the highest RSSI.
- Keep `mqtt_ha_enabled = false` (the default) in DragonSync's `config.ini` to avoid duplicate entities. If you previously turned it on, set it back to `false` and restart DragonSync.

---

## Automation examples

**Notify when any drone enters my house zone:**

```yaml
alias: WarDragon — drone in house zone
trigger:
  - platform: zone
    event: enter
    zone: zone.house
    entity_id:
      - device_tracker.drone_f6q8d244c00cl2kf_position
action:
  - service: notify.notify
    data:
      title: WarDragon
      message: "Drone in house zone"
```

**Strobe lights on a strong FPV signal:**

```yaml
alias: WarDragon — strong FPV warning
trigger:
  - platform: event
    event_type: wardragon_signal_detected
condition:
  - "{{ trigger.event.data.signal_type == 'fpv' }}"
  - "{{ trigger.event.data.rssi | float(-200) > -60 }}"
action:
  - service: light.turn_on
    target:
      entity_id: light.alert_strip
    data:
      rgb_color: [255, 50, 0]
      flash: short
```

---

## Troubleshooting

- **No devices appear**: check the HA MQTT integration is loaded and connected. Then check `mosquitto_sub -t 'wardragon/#' -v` from the same network — you should see `wardragon/system/<kit_id>/attrs` and `wardragon/drones` traffic. If you see `wardragon/system/attrs` (no kit_id segment) instead, your DragonSync is on the legacy single-kit schema and needs upgrading to v2.0+.
- **"Mqtt required" error in config flow**: install the official [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) before WarDragon.
- **Drone marker stuck at the equator**: this means DragonSync sent `lat=0, lon=0` (no GPS fix). The integration filters these out and marks the tracker unavailable; if you see a marker, the filter regressed — file an issue.
- **Kit shows in the device list but not on the map**: prior to v0.3.0 the kit position tracker required `gps_fix: true`. Static-coordinate kits (no GPSd, `time_source: static`) were hidden. v0.3.0+ shows the kit at its published coords regardless; the `binary_sensor.<kit>_gps_fix` is still available for automations that care about fix quality.
- **COP card shows "Configuration error" on cold load**: the bundle is loaded via dynamic `import()` and occasionally resolves after the dashboard tries to instantiate it. One hard-refresh later it's cached and the race is gone. If it consistently fails to load across multiple refreshes, a stale service worker is usually the culprit — reset it from the browser console:
  ```js
  navigator.serviceWorker.getRegistrations().then(rs => Promise.all(rs.map(r => r.unregister()))).then(() => location.reload(true));
  ```
- **COP card not in the picker**: hard-refresh the browser (Ctrl-F5). Home Assistant caches frontend resources; a hard refresh forces it to pick up the auto-registered card module after first install. If it's still missing, add it via the **Manual** card option at the bottom of the picker with `type: custom:wardragon-cop-card` — the picker occasionally hangs on the "Custom cards" loading state even when the card is registered globally.
- **Per-kit availability seems wrong**: requires DragonSync v2.0+. v1 had a single `wardragon/system/availability` topic shared across kits.
- **Temperatures display as 125+ raw numbers**: fixed in v0.3.0. Earlier builds didn't declare `native_unit_of_measurement` on the temperature sensors, so HA rendered Celsius values without a unit and (depending on operator locale) auto-converted them to Fahrenheit without the label. Upgrade.

For the canonical end-to-end install walkthrough (HACS install, `auto-entities` card, side-by-side dashboard YAML), see [docs/INSTALL.md](docs/INSTALL.md). For alternative dashboard layouts (tabbed, panel/wallboard, per-drone follow), see [docs/DASHBOARDS.md](docs/DASHBOARDS.md).

---

## Architecture

The integration is a thin HA-side adapter on top of DragonSync's MQTT schema. Coordinator owns state; subscriber translates topics. The wire format is the [DragonSync MQTT schema](https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md), which is the canonical source.

```
custom_components/wardragon/
├── __init__.py             # async_setup_entry / async_unload_entry
├── manifest.json
├── const.py                # signals, topic helpers/parsers, defaults
├── config_flow.py          # GUI config + options flow
├── coordinator.py          # WarDragonCoordinator: state + lifecycle + fusion
├── mqtt_client.py          # WarDragonMQTTSubscriber: subscribe + dispatch
├── models.py               # Frozen Kit, Drone, Signal dataclasses
├── entity.py               # Base classes for kit / drone / kit-signal entities
├── sensor.py / sensor_definitions.py
├── binary_sensor.py
├── device_tracker.py       # Drone, pilot, home, kit, signal trackers
├── button.py               # Clear drone button
├── services.py / services.yaml
├── diagnostics.py
├── repairs.py
├── frontend.py             # Auto-registers the COP custom card
├── strings.json / translations/en.json
├── brand/                  # icon.png + logo.png (256/512)
├── frontend/               # COP card (TypeScript + Lit + Rollup)
│   ├── package.json
│   ├── rollup.config.mjs
│   ├── tsconfig.json
│   ├── src/
│   │   ├── wardragon-cop-card.ts
│   │   ├── types.ts
│   │   ├── utils/ha-helpers.ts
│   │   └── styles/theme.ts
│   └── dist/               # Built bundle (gitignored; built in release CI)
└── blueprints/automation/wardragon/
    ├── notify_drone_in_zone.yaml
    ├── notify_drone_lost.yaml
    ├── notify_kit_offline.yaml
    └── notify_signal_detected.yaml
```

---

## Roadmap

- **v0.1.0** (shipped) — drones, kits, signals, multi-kit fusion, services, blueprints, options, diagnostics, repairs, brand assets.
- **v0.2.0** (current) — bundled COP custom Lovelace card.
- **v0.3.0** (planned) — ADS-B aircraft entities (filtered by altitude / range), HTTP API supplement for restart-resume, statistics/history (drone-sightings-per-band-per-day).
- **v0.4.0** (planned) — PTZ camera slew service: `wardragon.slew_camera_to_drone` computes azimuth/elevation/zoom from camera GPS+heading offset to drone position, calls ONVIF `camera.move`. Multi-camera "closest with line-of-sight" picker. Lead-time compensation using drone velocity.

---

## Links

- **WarDragon** — [github.com/alphafox02/WarDragon](https://github.com/alphafox02/WarDragon)
- **DragonSync** — [github.com/alphafox02/DragonSync](https://github.com/alphafox02/DragonSync)
- **DragonSync MQTT schema** — [docs/mqtt-schema.md](https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md)
- **Issue tracker** — [github.com/alphafox02/WarDragon-HA-Integration/issues](https://github.com/alphafox02/WarDragon-HA-Integration/issues)

---

## License

MIT — see [LICENSE](LICENSE).
