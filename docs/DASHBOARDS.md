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
      - entity_id: "device_tracker.wardragon_*_position"
      - entity_id: "device_tracker.drone_*_position"
      - entity_id: "device_tracker.drone_*_pilot"
      - entity_id: "device_tracker.drone_*_home"
      - entity_id: "zone.home"
    exclude:
      - state: "unavailable"
      - state: "unknown"
  grid_options:
    columns: full
    rows: 12
```

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
