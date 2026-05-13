# Dashboard recipes

[INSTALL.md](INSTALL.md) walks you through the default setup: COP card on the left, auto-discovering map on the right, using HACS `auto-entities` to wrap the map. That's the layout most operators end up running.

This doc covers alternatives for operators who want a different layout or don't want to install `auto-entities`.

---

## Tabbed dashboard (no HACS dep for the map)

If you don't want `auto-entities`, you can get auto-discovery on the map for free by giving the map its own dashboard view and using HA's built-in `map` strategy — the same one that powers HA's sidebar "Map" dashboard.

```yaml
title: WarDragon
views:
  - title: COP
    path: cop
    icon: mdi:radar
    cards:
      - type: custom:wardragon-cop-card

  - title: Map
    path: map
    icon: mdi:map
    strategy:
      type: map
```

Two tabs at the top of the dashboard: **COP** and **Map**. No HACS dependency, no entity list to maintain. The trade is a click to switch tabs instead of seeing both at once.

Caveat: HA's built-in `map` strategy auto-discovers **every** `device_tracker` with location attributes — not just WarDragon ones. If your HA also tracks phones, cars, or other people via Mobile App / iCloud / GPSLogger, those markers also show up on this tab. If you want a WarDragon-only map view, use the default side-by-side layout from [INSTALL.md](INSTALL.md) which filters by entity_id glob.

---

## Panel / wallboard mode (for a kiosk or wall-mounted tablet)

For an operator wall-mount where the dashboard fills the entire screen and there's no HA chrome, use `panel: true` on the view. Combine with `auto-entities` so it stays current as drones come and go.

```yaml
title: WarDragon Wallboard
views:
  - title: Wall
    path: wall
    icon: mdi:radar
    panel: true
    cards:
      - type: custom:auto-entities
        card:
          type: map
          default_zoom: 13
          aspect_ratio: "16:9"
          hours_to_show: 4
        filter:
          include:
            - entity_id: "device_tracker.wardragon_*_position"
            - entity_id: "device_tracker.drone_*_position"
          exclude:
            - state: "unavailable"
            - state: "unknown"
```

`panel: true` makes the single card fill the whole view. `hours_to_show: 4` leaves a longer trail than the default 1 hour, which is more useful when the wallboard is meant to show recent activity at a glance.

If you want both the COP and the map on the wallboard, drop `panel: true` and use the sections layout from [INSTALL.md](INSTALL.md) with the COP and map cards side by side.

---

## Per-drone "follow" view

For an exercise or after-action review of a specific drone, you sometimes want one drone's full telemetry visible alongside its position. Add a separate view to the WarDragon dashboard:

```yaml
- title: Track
  path: track
  cards:
    - type: vertical-stack
      cards:
        - type: map
          default_zoom: 16
          aspect_ratio: "4:3"
          entities:
            - device_tracker.drone_<drone_id>_position
            - device_tracker.drone_<drone_id>_pilot
            - device_tracker.drone_<drone_id>_home
        - type: entities
          title: Drone telemetry
          entities:
            - sensor.drone_<drone_id>_rssi
            - sensor.drone_<drone_id>_altitude
            - sensor.drone_<drone_id>_speed
            - sensor.drone_<drone_id>_heading
            - sensor.drone_<drone_id>_protocol_family
            - sensor.drone_<drone_id>_frequency_band
            - sensor.drone_<drone_id>_operator_id
            - sensor.drone_<drone_id>_caa_registration
```

Replace `<drone_id>` with the actual drone_id from the integration. This view stops auto-updating its entity list (since you're pinning a specific drone), but for incident review that's the point.

---

## Live map ↔ history map toggle

HA's recorder logs every drone / kit position transition automatically. The stock `map` card has an `hours_to_show` option that draws trail lines from that history. Putting a toggle between a "live" map (current positions, no trails) and a "history" map (last N hours of trails) is pure Lovelace YAML — no integration code needed.

Useful when you want to flip back and forth between "where is everything right now" and "where has this drone been."

### Helpers to create first

In Home Assistant: **Settings → Devices & Services → Helpers → Create helper**.

1. **Toggle** — type `Toggle`, name `WarDragon — show drone history`. Resulting entity_id: `input_boolean.wardragon_show_drone_history`.
2. **Dropdown** — type `Dropdown`, name `WarDragon — history window`, options `1`, `6`, `24`, `72`. Resulting entity_id: `input_select.wardragon_history_window`.

### Dashboard YAML

Drop this into a section in your existing dashboard. It uses [`auto-entities`](https://github.com/thomasloven/lovelace-auto-entities) so new kits and drones populate automatically.

```yaml
- type: entities
  entities:
    - entity: input_boolean.wardragon_show_drone_history
      name: Show drone history
    - entity: input_select.wardragon_history_window
      name: History window (hours)

# LIVE map — shown when the toggle is off
- type: conditional
  conditions:
    - entity: input_boolean.wardragon_show_drone_history
      state: "off"
  card:
    type: custom:auto-entities
    card:
      type: map
      default_zoom: 14
      hours_to_show: 0
      aspect_ratio: "16:10"
    filter:
      include:
        - entity_id: "device_tracker.wardragon_*_position"
        - entity_id: "device_tracker.drone_*_position"
        - entity_id: "zone.home"
      exclude:
        - state: "unavailable"
        - state: "unknown"

# HISTORY maps — one per supported window. The dropdown picks which
# conditional card renders. Pure conditional-card switching is needed
# because the stock map card doesn't accept a templated hours_to_show.
- type: conditional
  conditions:
    - entity: input_boolean.wardragon_show_drone_history
      state: "on"
    - entity: input_select.wardragon_history_window
      state: "1"
  card:
    type: custom:auto-entities
    card: { type: map, default_zoom: 14, hours_to_show: 1, aspect_ratio: "16:10" }
    filter:
      include:
        - entity_id: "device_tracker.wardragon_*_position"
        - entity_id: "device_tracker.drone_*_position"

- type: conditional
  conditions:
    - entity: input_boolean.wardragon_show_drone_history
      state: "on"
    - entity: input_select.wardragon_history_window
      state: "6"
  card:
    type: custom:auto-entities
    card: { type: map, default_zoom: 14, hours_to_show: 6, aspect_ratio: "16:10" }
    filter:
      include:
        - entity_id: "device_tracker.wardragon_*_position"
        - entity_id: "device_tracker.drone_*_position"

- type: conditional
  conditions:
    - entity: input_boolean.wardragon_show_drone_history
      state: "on"
    - entity: input_select.wardragon_history_window
      state: "24"
  card:
    type: custom:auto-entities
    card: { type: map, default_zoom: 14, hours_to_show: 24, aspect_ratio: "16:10" }
    filter:
      include:
        - entity_id: "device_tracker.wardragon_*_position"
        - entity_id: "device_tracker.drone_*_position"

- type: conditional
  conditions:
    - entity: input_boolean.wardragon_show_drone_history
      state: "on"
    - entity: input_select.wardragon_history_window
      state: "72"
  card:
    type: custom:auto-entities
    card: { type: map, default_zoom: 14, hours_to_show: 72, aspect_ratio: "16:10" }
    filter:
      include:
        - entity_id: "device_tracker.wardragon_*_position"
        - entity_id: "device_tracker.drone_*_position"
```

### Why this works without integration changes

- Every drone / kit `device_tracker` reports its state automatically as `home`, `not_home`, or a zone name based on its current lat/lon. HA's recorder logs each state transition.
- `hours_to_show: N` on the `map` card asks HA's history API for that entity's positions over the last `N` hours and draws trail lines connecting them.
- When a drone goes silent past the integration's inactivity timeout (default 5 min), its tracker flips to `unavailable`. The prior position history is still in the recorder and still plotted by `hours_to_show` — the trail just stops where the live updates stopped. When the drone resumes broadcasting, the trail picks up from the new position.
- The history window is bounded by HA's `recorder.purge_keep_days` setting (default 10 days). For longer retention, increase that in `configuration.yaml`.
