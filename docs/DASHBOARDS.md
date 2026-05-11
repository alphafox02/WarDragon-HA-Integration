# Dashboard recipes

The README's "Suggested dashboard layout" works for a single static install — manual entity list, COP on the left, map on the right. When kits and drones come and go you'd be editing YAML by hand.

This doc covers the one alternative most operators end up wanting: an auto-discovering map that doesn't need maintenance.

---

## Auto-discovering map (no entity list to maintain)

Native HA `map` takes a hard-coded entity list. The community card [`auto-entities`](https://github.com/thomasloven/lovelace-auto-entities) (installed via HACS) wraps any card and rebuilds its entity list from filters every state change. New kit publishes → entity appears → filter matches → map updates. No code changes when adding kits or as drones come and go.

### Install auto-entities

1. Open HACS → **Frontend** (or **Plugins** on older HACS).
2. Three-dot menu → **Custom repositories** is *not* needed — `auto-entities` is in the default HACS index.
3. Click **Explore & download repositories**, search **auto-entities**, pick **Lovelace auto-entities** by Thomas Lovén.
4. **Download** → accept defaults.
5. Reload the browser (HA does not need to restart for frontend resources).

### Use it for the map

Swap the `map` card in the README's suggested dashboard for this:

```yaml
- type: custom:auto-entities
  card:
    type: map
    default_zoom: 14
    hours_to_show: 1
    aspect_ratio: "16:10"
  filter:
    include:
      # Kit position + current-signal-channel tracker (both end in _position)
      - entity_id: "device_tracker.wardragon_*_position"
      # Drone main + pilot + home trackers (all end in _position):
      #   device_tracker.drone_<id>_position
      #   device_tracker.drone_<id>_pilot_position
      #   device_tracker.drone_<id>_home_position
      - entity_id: "device_tracker.drone_*_position"
      - entity_id: "zone.home"
    exclude:
      - state: "unavailable"
      - state: "unknown"
  grid_options:
    columns: full
    rows: 12
```

Note that `device_tracker.drone_*_position` is a single glob that already catches the drone's main, pilot, and home trackers — they all share the `_position` suffix from the integration's `EntityDescription` keys. You don't need separate filter lines for pilot and home.

---

## Tabbed dashboard (no HACS dep)

If you don't want to install `auto-entities`, you can get auto-discovery for free by giving the map view its own tab and using HA's built-in `map` strategy (the same one that powers HA's sidebar "Map" dashboard):

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

Two tabs: **COP** and **Map**. No HACS dependency, no entity list to maintain. The cost is a click to switch tabs instead of side-by-side viewing.

Caveat: the built-in `map` strategy auto-discovers **every** `device_tracker` entity on the HA install that has location attributes — not just WarDragon ones. If your HA also tracks phones, cars, or other people via Mobile App / iCloud / GPSLogger, those markers will appear on this tab too. If you want a WarDragon-only map, use the `auto-entities` approach above with explicit filters.
