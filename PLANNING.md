# WarDragon HA Integration — Planning Doc

**Audience:** future development sessions. Self-contained — read this and you have everything needed to start work without the conversation it came from.

**Last updated:** 2026-05-09 (v2 branch pushed; Console deferred)

---

## Current state (read this first)

**DragonSync v2 multi-kit MQTT branch is PUSHED to GitHub:** [feature/multi-kit-v2](https://github.com/alphafox02/DragonSync/tree/feature/multi-kit-v2)

Status of upstream dependency:

- DONE: kit-id cache landed on `main` (commit `f4b59af`) — provides fast warm-boot startup via `/var/lib/wardragon/kit-id`
- DONE: `mqtt_sink.py` kit-scoping committed on branch (commit `f900ea1`)
- DONE: `dragonsync.py` wires `kit_id_provider` to MqttSink (commit `3d078ed`)
- DONE: `docs/mqtt-schema.md` updated for v2 (commit `4575c4f`)
- DONE: All 130 unit tests passing locally
- PENDING: real-kit smoke test before merge to main
- PENDING: branch not yet merged to main

**Schema is FINAL** — design discussion is over. The wire format on the v2 branch is what this integration consumes. See the canonical schema reference: [docs/mqtt-schema.md](https://github.com/alphafox02/DragonSync/blob/feature/multi-kit-v2/docs/mqtt-schema.md) on the branch.

**Sequencing has changed:** Console v0.1 is **deferred indefinitely**. The updated order is:

1. DONE: kit-id cache (on main)
2. DONE: DragonSync v2 multi-kit MQTT (on branch, awaiting kit test + merge)
3. PENDING: real-kit smoke test, then merge v2 to main
4. PENDING: docs refresh (operator-facing WarDragon docs updated for v2)
5. **PENDING: this HA integration v0.1** (starts after step 4)
6. Console comes later, after HA integration

Implementation of this integration can begin once step 4 lands — no need to wait for Console.

---

## Critical dependency: DragonSync v2.0 release

**This integration is built against DragonSync v2.0** (currently on `feature/multi-kit-v2` branch, will be on `main` after merge).

DragonSync's v1 MQTT topic schema breaks in multi-kit deployments — system/service availability topics aren't kit-scoped, so two kits sharing a broker stomp each other's retained state. The v2 branch redesigns the topic structure to scope kit-level state per-kit.

**Schema this integration consumes (post-v2):**

| Topic | Purpose |
|---|---|
| `wardragon/system/<kit_id>/attrs` | Per-kit telemetry (CPU, mem, GPS, SDR temps) |
| `wardragon/system/<kit_id>/state` | Per-kit textual state |
| `wardragon/system/<kit_id>/availability` | Per-kit kit-telemetry-flowing flag |
| `wardragon/service/<kit_id>/availability` | Per-kit DragonSync process LWT |
| `wardragon/drone/<drone_id>` | Per-drone state (cooperative across kits — not kit-scoped) |
| `wardragon/drones` | Aggregate drone stream (`seen_by` payload field carries kit attribution) |
| `wardragon/signals/<seen_by>` | Per-kit signal feed (already kit-scoped via `seen_by` segment) |

**HA discovery in v2:** DragonSync publishes per-kit system devices (`wardragon_drone_<kit_id>_system_*`) and per-drone device_trackers (drone_id-keyed, shared across kits). Multi-kit drone fusion happens at the integration layer: this integration subscribes to the standard drone topics (drone_id-keyed) and merges per-kit observations using the `seen_by` payload field.

**Strategy: stock HA AND custom integration both supported.** Stock HA users (using DragonSync's auto-discovery without this integration) get a working multi-kit experience after v2 — each kit appears as its own HA device, drones as standard device_trackers. This integration adds the polish layer on top: multi-kit drone fusion, custom services, lifecycle management, automation blueprints, custom Lovelace cards. Mutual exclusion via a future `mqtt_ha_native_mode` config flag in DragonSync (added when this integration ships, so DragonSync's auto-discovery defers to the integration when both are present).

---

## What we're building

A native Home Assistant custom integration (HACS-distributable) for WarDragon drone detection kits.

**Why this exists:**
DragonSync (the service running on every WarDragon kit) already publishes MQTT auto-discovery messages, so plain HA users get device_trackers and basic sensors today. That covers the "data flows to HA" need but is missing the polish layer: custom services, multi-kit fusion, drone lifecycle (purge stale, manual clear), automation blueprints, and a branded surveillance dashboard. This integration is that polish layer.

**Why we're not just consuming a competitor's integration:**
A commercial product (DECTYR RX-5) ships an HA integration that does most of this for their hardware. We considered:
- **Bridge / translator sink** — DragonSync would republish on their topic schema. Rejected because it advertises their hardware to WarDragon users.
- **Fork their integration** — MIT-licensed so legal, but their schema, hardware-specific firmware update logic, and trademarks would require ~40% rewrite. Closer to a from-scratch build using their structure as scaffolding.
- **Build our own** — picked. Sovereignty over branding, schema, UX. Their codebase is reference material, not a code source.

We're using their repo at `/home/dragon/Downloads/ha-integration/` as a **structural reference** (architecture patterns, dataclass model design, coordinator/MQTT subscriber separation, sensor definition style) but not lifting code. If we ever do lift a non-trivial pattern, attribute inline at that location — don't put it in the user-facing README.

---

## Naming & structure

| Thing | Value |
|-------|-------|
| Repo name (GitHub) | `alphafox02/WarDragon-HA-Integration` (parallels `WarDragon-ATAK-Plugin-Source`) |
| Local path | `/home/dragon/WarDragon/WarDragon-HA-Integration/` |
| HA integration domain | `wardragon` (lowercase, no hyphens — HA convention) |
| HACS display name | "WarDragon" |
| Custom services | `wardragon.clear_drone`, `wardragon.export_drones`, etc. |
| Events | `wardragon_drone_detected`, `wardragon_drone_lost`, etc. |

The HA domain `wardragon` aligns with `mqtt_ha_device_base = wardragon_drone` already used in DragonSync's `sinks/mqtt_sink.py`, so entity names stay consistent (`device_tracker.wardragon_<id>`, `sensor.wardragon_<id>_alt`).

---

## Scope

### In scope for v0.1

1. **Drone telemetry** — every field DragonSync publishes (52 fields per [mqtt-schema.md](https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md)) surfaced as device + sensors per drone.
2. **Kit telemetry** — WarDragon kit as an HA device with CPU/mem/GPS/SDR-temps sensors.
3. **Pilot & home location** — separate device_trackers per drone (matches existing DragonSync MQTT discovery).
4. **DroneID protocol detail** — DJI O2/O3/O4 markers in drone description (just landed in `dji_receiver.py` commit `e703208`); shown as a sensor or device attribute.
5. **Signal detections** — FPV / RF alerts published to `wardragon/signals` as first-class entities. **DECTYR doesn't have this** — it's an exceed point.
6. **Lifecycle** — drone inactivity timeout, stale purge, manual clear via service.
7. **Custom services** — `clear_drone`, `export_drones`, possibly `send_command` if we expose any kit control via DragonSync's HTTP API.
8. **Multi-kit fusion** — when two kits see the same drone, merge into one HA device with per-kit RSSI attributes.
9. **Three blueprints** — `notify_drone_in_zone`, `notify_drone_lost`, `notify_kit_offline`.
10. **Strict payload validation** — like DECTYR's `models.py`, drop malformed payloads with a debug log; don't crash.

### Deferred to a later phase

- **ADS-B aircraft entities** — DragonSync publishes them on `wardragon/aircraft`, but volume is high and most operators don't want every airliner as an HA entity. Add later as opt-in with aggressive filters (e.g. only altitude < X, only within Y km).
- **Custom Lovelace cards** — surveillance card and map card. Probably a separate repo (`WarDragon-HA-Cards`) since HACS treats frontend cards as a separate category. Could ship later.
- **FAA RID lookup display** — DragonSync exposes `rid_make`, `rid_model`, etc.; surface them in v0.2 once core entities are stable.
- **Kit firmware control** — DECTYR exposes reboot/firmware-update buttons. Out of scope; we don't have the equivalent control plane in DragonSync today.

### Explicitly out of scope (for now)

- Replacing DragonSync's existing MQTT auto-discovery. We **augment**, then operators flip a flag (see "Coexistence" below) to switch to native mode if they want.
- Hardware-specific control (DECTYR has reboot/log retrieval/firmware slot management for their device).
- Cloud connectivity / external services.

---

## Coexistence with existing DragonSync MQTT auto-discovery

DragonSync's `sinks/mqtt_sink.py` already publishes `homeassistant/sensor/<id>/config` discovery messages that create entities. After v2 these are kit-scoped (each kit registers as its own HA device). If we ship a native integration, we have three coexistence options.

**DECISION: Option A** (mutual exclusion via `mqtt_ha_native_mode` flag in DragonSync). The flag defaults to `false` — stock HA users (no custom integration) continue to get DragonSync's auto-discovery. Operators who install this integration set the flag to `true`, DragonSync stops publishing discovery configs, and the integration owns entity creation.

The flag is added to DragonSync as part of THIS integration's release (not v2.0). When v2.0 is the latest release and this integration doesn't yet exist, DragonSync always publishes auto-discovery (current behavior).

### Option A: Mutual exclusion (single config flag) — CHOSEN

Add one line to DragonSync's `config.ini`:

```ini
[SETTINGS]
# Use the native WarDragon HA integration (HACS) instead of plain MQTT auto-discovery.
# When true, DragonSync stops publishing homeassistant/* discovery configs;
# the integration handles entity creation and gives you services, lifecycle, blueprints.
mqtt_ha_native_mode = false
```

**Behavior:**
- `false` (default) — current behavior. Plain MQTT discovery. No integration needed. Existing users unaffected.
- `true` — DragonSync skips publishing `homeassistant/*` configs. Operators install the integration via HACS, which discovers WarDragon kits via the existing `wardragon/system/availability` and `wardragon/drones` topics.

**Pros:** Predictable. No duplicate entities. Backward compatible (default false). Single switch for operators.
**Cons:** Operators have to flip a flag. Mode change requires restart of DragonSync to clear retained discovery messages.

### Option B: Augment mode (no flag, both run together)

Integration adds **services** and **lifecycle** but doesn't create its own entities. Plain MQTT discovery does that.

**Pros:** No flag, no migration story.
**Cons:** Hard to reason about — what owns what? Services like "clear drone" can't really clear an entity that DragonSync re-publishes. Multi-kit fusion is impossible because DragonSync's discovery creates a separate device per kit/drone tuple.

### Option C: Auto-detect (integration disables DragonSync's discovery via a heartbeat topic)

Integration publishes `wardragon/integration/active` with retain. DragonSync subscribes; if the topic is set, it suppresses its own HA discovery.

**Pros:** Zero operator config.
**Cons:** Magic. Hard to debug. If integration is uninstalled, DragonSync needs to detect that (LWT on the integration's topic), which is fragile across HA restarts.

**Recommended:** Option A. Explicit, reversible, easy to support.

---

## Data sources

The integration can consume data from two places. Both have trade-offs.

### 1. MQTT (primary)

**Topics consumed** (full schema: https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md):

- `wardragon/drones` — aggregate drone updates (one message per drone update)
- `wardragon/drone/<id>` — per-drone state (when DragonSync's `mqtt_per_drone_enabled = true`)
- `wardragon/drone/<id>/availability` — drone online/offline
- `wardragon/system/attrs` — kit telemetry
- `wardragon/system/availability` — kit online/offline
- `wardragon/signals` — FPV/RF alerts (when `mqtt_signals_enabled = true`)
- `wardragon/service/availability` — DragonSync process online/offline (LWT)

**Pros:** Push model, low latency, minimal load on DragonSync, multi-kit auto-discovery is natural (one topic per kit).
**Cons:** Need to track lifecycle (last-seen) ourselves; MQTT retain semantics interact with HA restart.

### 2. HTTP API (secondary, optional)

DragonSync's HTTP API at `api/api_server.py`:
- `GET /drones` — list of drones (calls `manager.export_tracks()` → `Drone.to_dict()`, which already includes `description`, `transport`, etc.)
- `GET /status` — kit status
- `GET /signals` — signal alerts
- `GET /config` — DragonSync config (read-only)

**Pros:** Pull model — perfect for filling gaps after HA restart. Includes RID lookup fields we might not always get on MQTT.
**Cons:** Polling overhead. Each kit needs its IP discovered (mDNS? config?). Doesn't scale well to many kits.

**Recommendation for v0.1:** MQTT primary, HTTP optional/later. If a kit's HTTP endpoint is reachable, augment with `GET /drones` for the initial state on HA startup.

---

## Architecture sketch

Mirror standard HA custom integration structure:

```
custom_components/wardragon/
├── __init__.py            # async_setup_entry, async_unload_entry
├── manifest.json
├── const.py               # domain, defaults, signals, topic helpers
├── config_flow.py         # GUI setup: MQTT prefix, kit discovery
├── coordinator.py         # WarDragonCoordinator: drone registry, lifecycle, multi-kit fusion
├── mqtt_client.py         # MQTTSubscriber: subscribe to wardragon/* topics
├── models.py              # Dataclasses: Kit, Drone, Signal (strict validation)
├── sensor.py              # Drone + kit + signal sensor platforms
├── binary_sensor.py       # online/offline binary sensors
├── device_tracker.py      # Drone + pilot + home + kit trackers
├── button.py              # "Clear drone" button per drone
├── services.py            # clear_drone, export_drones
├── services.yaml          # Service schema for HA UI
├── strings.json           # English UI strings
├── icon.png               # Branding (TODO — need WarDragon logo asset)
├── logo.png               # Branding (TODO)
├── translations/
│   └── en.json
└── blueprints/
    └── automation/wardragon/
        ├── notify_drone_in_zone.yaml
        ├── notify_drone_lost.yaml
        └── notify_kit_offline.yaml
```

**Design patterns to borrow** (from DECTYR's structure — pattern, not code):
- **Coordinator + subscriber separation** — MQTT subscriber is dumb (parse + dispatch), coordinator owns state and merges multi-source updates.
- **Frozen dataclass models with `from_dict` constructors** — drop invalid payloads with a warning, never crash.
- **ODID-style enum normalisation** — accept both numeric and symbolic forms (DragonSync uses human-readable strings; we may want a normalised form for HA template compatibility).
- **Per-domain HA platforms** — one file per platform (sensor.py, binary_sensor.py, etc.). HA convention.

**Design choices to make differently:**
- DECTYR's required-field set assumes their hardware: `scanner_id`, `mac`, `broadcast_protocol`, `signal_type`, `complete`, `rssi`, `timestamp`. Our required set should match what DragonSync **actually always emits** — `id`, `lat`, `lon`, `track_type`. Everything else conditional.
- DECTYR rejects payloads missing required fields; we should be more forgiving — log + carry on with what we have. WarDragon supports partial RID broadcasts (e.g., Basic ID without Location/Vector yet).

---

## Wire format reference

Authoritative schema lives at: https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md

Key fields the integration must handle (subset — see schema for full list):

**Drone payload:**
- `id` (always, drone identifier)
- `description` (always; DJI O4/O3/O2 markers, operator self-ID text — exceed point: parse and surface protocol family separately)
- `lat`, `lon`, `latitude`, `longitude` (always; HA-friendly mirrors)
- `alt`, `height`, `speed`, `vspeed`, `direction`, `rssi` (always)
- `pilot_lat`, `pilot_lon`, `home_lat`, `home_lon` (always; 0.0 when not detected — handle as "no fix")
- `mac`, `id_type`, `caa_id`, `operator_id`, `ua_type`, `ua_type_name` (conditional)
- `freq`, `freq_mhz`, `transport` (conditional; transport empty for OcuSync)
- `rid_make`, `rid_model`, `rid_status`, `rid_lookup_success` (conditional, only when FAA RID lookup ran)
- `seen_by` (always when published; identifies which kit observed it — critical for multi-kit fusion)

**Kit (`wardragon/system/attrs`):**
- `id`, `latitude`, `longitude`, `hae`, `cpu_usage`, `memory_total_mb`, `memory_available_mb`
- `temperature_c`, `pluto_temp_c`, `zynq_temp_c`, `uptime_s`, `gps_fix`

**Signal (`wardragon/signals`):**
- `uid`, `signal_type`, `source`, `callsign`, `description`
- `lat`, `lon`, `radius_m`, `seen_by`
- `center_hz`, `bandwidth_hz`, `rssi`

---

## Where to "exceed" DECTYR

These are differentiators that make this integration WarDragon-specific value:

1. **DroneID protocol family entity** — surface `O2`/`O3`/`O4`/`OcuSync`/`WiFi-NaN`/`BT5-LR` as a discrete sensor or device attribute. Parsed from `description` field. WarDragon's strength is broad RF coverage; HA dashboards should reflect that.
2. **Signals as first-class** — DECTYR has zero signal-detection plumbing. WarDragon's FPV / RF alerts deserve their own entity type, dashboard tile, and blueprint.
3. **Frequency awareness** — DECTYR doesn't surface `freq_mhz` per drone meaningfully. We can group drones by band (2.4 / 5.2 / 5.8 GHz) and let operators automate on band-specific alerts.
4. **DJI OcuSync home/pilot points** — DECTYR's operator point is RID-spec only. DragonSync exposes pilot AND home points (DJI-specific), and we already have separate trackers.
5. **CAA registration** — `caa_id` field surfaced per-drone (some EU compliance use cases).

---

## Testing strategy

- HA is on the user's local network → can deploy and test live.
- Unit tests for `models.py` (payload parsing) using fixture payloads from real DragonSync output.
- Integration tests with `pytest-homeassistant-custom-component` for config flow and entity registration.
- A **golden-path** test that ingests our [example payload from mqtt-schema.md](https://github.com/alphafox02/DragonSync/blob/main/docs/mqtt-schema.md#example-payload) and verifies HA entities appear with expected states.

---

## Roadmap (rough)

### Phase 1 — Bones (target: 1–2 dev sessions)
- [ ] `manifest.json`, `const.py`, `config_flow.py` (MQTT prefix as input)
- [ ] `mqtt_client.py` — subscribe to `wardragon/drones`, `wardragon/system/attrs`
- [ ] `models.py` — `Kit`, `Drone`, `Signal` dataclasses with `from_dict`
- [ ] `coordinator.py` — single-kit drone tracking, lifecycle (no fusion yet)
- [ ] `device_tracker.py`, `sensor.py` — drone + kit basic entities
- [ ] Integration installs cleanly; one drone shows up; can see it on the HA map

### Phase 2 — Polish
- [ ] Multi-kit fusion (merge by `id`, attribute per-kit RSSI)
- [ ] Pilot + home device_trackers
- [ ] Custom services: `clear_drone`, `export_drones`
- [ ] Blueprints (3)
- [ ] Strings/translations
- [ ] DragonSync `mqtt_ha_native_mode` flag — coordinate with main DragonSync repo PR

### Phase 3 — Signals
- [ ] Signal subscriber + signal entity model
- [ ] Signal-specific blueprints

### Phase 4 — Distribution
- [ ] HACS submission (custom repo first; default catalog later)
- [ ] WarDragon docs page linking to HACS install
- [ ] Branding assets (icon.png, logo.png) — need to coordinate with overall WarDragon brand

### Phase 5 — Later
- [ ] ADS-B aircraft entities (filtered)
- [ ] Custom Lovelace cards (separate repo `WarDragon-HA-Cards`)
- [ ] HTTP API supplement for restart-resume

---

## Open questions for next session

1. **Branding assets** — does the WarDragon project have a finalised logo/icon at the size HA wants (256x256 PNG, transparent BG)? If not, sketch placeholders and replace later.
2. **Config flow input** — beyond MQTT prefix, do we need the broker host/credentials? Or rely entirely on HA's existing MQTT integration (the way DECTYR does)? **Decision:** rely on HA's MQTT integration. Don't reinvent.
3. **Multi-kit identity** — when two kits see the same drone with the same `id`, is the drone *really* the same? Yes for most Remote ID cases (serial number is unique). Fusion strategy: keep one HA device per drone `id`, store per-kit RSSI as attributes, take "best" position from highest-RSSI kit.
4. **What does "clear drone" do?** Just removes from HA registry, or sends a hint back to DragonSync to forget it? **Suggestion:** HA-side only for v0.1. DragonSync ages drones out on its own schedule.
5. **HACS submission timing** — wait until v1.0 (default catalog) or submit early as custom repo (URL-add)? **Suggestion:** custom repo from v0.1 so testers can install easily; submit to default catalog when stable.

---

## Coordination with DragonSync repo

Adding the `mqtt_ha_native_mode` flag is a DragonSync change, not an integration change. When we get to Phase 2:

1. PR to `alphafox02/DragonSync` adding the flag in `utils/config.py` and `sinks/mqtt_sink.py` (skip `_publish_ha_sensors` and `_publish_ha_device_tracker` when `True`).
2. PR to `alphafox02/WarDragon` docs adding a section explaining the trade-off ("if you install the WarDragon HACS integration, set this flag to true").

These two PRs and the v0.1 release of this integration should land together.

---

## Reference materials on disk

- DECTYR HA integration (architectural reference, not code source): `/home/dragon/Downloads/ha-integration/`
- DragonSync (the data producer): `/home/dragon/Downloads/ATAK-CIV-5.7.0.0-SDK/DragonSync/`
  - On `main`: v1 schema + kit-id cache (commit `f4b59af`)
  - On `feature/multi-kit-v2` branch: v2 multi-kit schema (target for this integration)
  - Run `git -C /home/dragon/Downloads/ATAK-CIV-5.7.0.0-SDK/DragonSync log --oneline -5` to see current state
- DragonSync v2 schema doc (canonical for this integration): `/home/dragon/Downloads/ATAK-CIV-5.7.0.0-SDK/DragonSync/docs/mqtt-schema.md` on the `feature/multi-kit-v2` branch
- WarDragon docs (operator guides): `/home/dragon/Downloads/WarDragon/`
- Internal planning docs (NOT in any repo, kept local): `/home/dragon/WarDragon/internal-planning/`
- WarDragon Console (deferred indefinitely): `/home/dragon/WarDragon/WarDragon-Console/`

---

## Future-session entry point

If you're picking this up cold, do this:

1. Read this file end-to-end.
2. Look at `/home/dragon/Downloads/ha-integration/custom_components/dectyr_rx5/` for structural reference.
3. Read `/home/dragon/Downloads/ATAK-CIV-5.7.0.0-SDK/DragonSync/docs/mqtt-schema.md` for the wire format you're consuming.
4. Confirm the open questions above with the user before writing code.
5. Start with Phase 1 (Bones).
