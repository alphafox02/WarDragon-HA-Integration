# Install and setup guide

End-to-end walkthrough for a fresh Home Assistant install. Following these steps gets you a working WarDragon dashboard with the **COP card on the left** and a **live, auto-discovering map on the right**, populated from a real DragonSync MQTT stream.

If you already have HA + HACS + the MQTT integration running, skip to step 3.

---

## 1. Prerequisites

- **Home Assistant 2024.1** or newer (any flavour: HAOS, HA Container, HA Supervised).
- **An MQTT broker** that DragonSync and Home Assistant can both reach. Mosquitto is the standard pick; it can run on the same box as HA or anywhere on the LAN.
- **DragonSync v2.0** or newer running on each WarDragon kit. v2.0 introduced the per-kit MQTT topic schema that this integration consumes.
- **HACS** installed in Home Assistant. If you don't have HACS yet, follow the installer at [hacs.xyz](https://hacs.xyz/docs/use/download/download/).

### Optional but recommended

- A static DHCP reservation for each WarDragon kit on your router so the kit IPs don't shift around.
- A dedicated MQTT user for WarDragon traffic, separate from your HA core MQTT user. Easier to audit and revoke later.

---

## 2. Set up the MQTT integration in Home Assistant

Required before WarDragon will work.

1. **Settings -> Devices & Services -> Add Integration**.
2. Search **MQTT** and click it.
3. Enter your broker's host, port (1883 unless you've changed it), username, and password.
4. Submit. The integration should connect immediately.

If MQTT was already connected, skip this step.

---

## 3. Install the WarDragon integration via HACS

1. Open **HACS** in the sidebar.
2. Three-dot menu (top right) -> **Custom repositories**.
3. Add this repo URL: `https://github.com/alphafox02/WarDragon-HA-Integration`
4. Category: **Integration**.
5. Click **Add**.
6. Back on the HACS main view, search **WarDragon**, click the card, then **Download**.
7. Accept defaults and **Download** again.
8. **Restart Home Assistant** (Settings -> System -> Restart).

After restart, the integration's Python is loaded but the integration entry hasn't been added yet. Next step does that.

---

## 4. Add the WarDragon integration entry

1. **Settings -> Devices & Services -> Add Integration**.
2. Search **WarDragon**, click it.
3. **MQTT topic prefix**: leave at the default `wardragon` unless your DragonSync is configured to publish under a different prefix.
4. **Submit**.

Within a few seconds you should see kit devices appear in the integration card. If you don't, see the Troubleshooting section in the main README — the most common cause is DragonSync not actually publishing yet, or publishing under a different topic prefix.

The **WarDragon COP** card is auto-registered at this point. It'll show up in the Lovelace card picker on any dashboard.

---

## 5. Install `auto-entities` (HACS frontend card)

This is the community card that wraps any built-in HA card and rebuilds its entity list from filter rules. We use it to wrap HA's `map` card so new kits and drones land on the map automatically as they come and go, without anyone editing dashboard YAML.

1. Open **HACS**.
2. Click **Explore & download repositories** (bottom right).
3. Search **auto-entities**, pick **Lovelace auto-entities** by Thomas Lovén.
4. **Download** -> accept defaults.
5. Reload the browser tab when prompted (HA itself does not need to restart for frontend resources).

---

## 6. Create the WarDragon dashboard

1. **Settings -> Dashboards** (left sidebar).
2. **+ Add Dashboard** (bottom right).
3. Pick **New dashboard from scratch**.
4. Title: **WarDragon**. Icon: `mdi:radar`. Click **Create**.
5. Open the new dashboard from the sidebar.
6. Top-right three-dot menu -> **Take control** (HA needs you to claim ownership of the dashboard before you can edit it).
7. Top-right three-dot menu -> **Edit dashboard** -> three-dot menu again -> **Raw configuration editor**.
8. Replace the entire contents with the YAML below, then click **Save** in the upper right.

```yaml
title: WarDragon
views:
  - title: Ops
    path: ops
    icon: mdi:radar
    type: sections
    max_columns: 4
    sections:
      - type: grid
        column_span: 1
        cards:
          - type: custom:wardragon-cop-card
            grid_options:
              columns: full
              rows: auto

      - type: grid
        column_span: 3
        cards:
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
                - entity_id: "zone.home"
              exclude:
                - state: "unavailable"
                - state: "unknown"
            grid_options:
              columns: full
              rows: 12
```

Close the editor and you should land on a dashboard that has the **COP card on the left** and an **auto-discovering map on the right**. As kits come online and drones get detected, they appear on both panels without further edits.

The `zone.home` filter rule keeps the map renderable when nothing's flying yet (you'll see a pin at your house). Drones that haven't acquired a real position (`lat=0, lon=0`) are filtered out by the `exclude: state unavailable` rule.

---

## 7. Verify it's working

1. Open `mosquitto_sub -h <broker> -u <user> -P <pass> -t 'wardragon/#' -v` from any machine on your network.
2. You should see at least:
   - `wardragon/system/<kit_id>/availability online` (retained, from each kit)
   - `wardragon/system/<kit_id>/attrs <JSON telemetry>` every ~30 seconds
3. In HA: **Settings -> Devices & Services -> WarDragon -> click the device card** to see the kit device and its entities. CPU, temperatures, uptime should all have live values.
4. On the WarDragon dashboard:
   - COP card shows the kit in the Kits tab.
   - Map shows the kit's position marker.
5. When a drone is detected (DragonSync publishes to `wardragon/drones`), it appears on the COP's Drones tab. Once the drone broadcasts a real GPS position, the map marker also appears.

---

## 8. Optional: tune lifecycle timeouts

The integration ships sensible defaults but they're tunable. Settings -> Devices & Services -> WarDragon -> **Configure**:

- **Drone inactivity timeout** — how long after the last drone packet before its tracker is marked unavailable. Default 300 s. Lower if you want drones to fall off faster after they fly away.
- **Drone purge after** — how long after going unavailable before the drone device is removed from HA entirely. Default 86400 s (24h). Lower to keep the device registry tidy if you see a lot of unique drones.
- **Kit offline timeout** — how long after the last kit telemetry before the kit is marked offline. Default 60 s.

---

## 9. Optional: load the automation blueprints

Four blueprints are bundled — `notify_drone_in_zone`, `notify_drone_lost`, `notify_kit_offline`, `notify_signal_detected`. Settings -> Automations & Scenes -> **Blueprints**: you should see them under the `wardragon` source. Click one to create an automation from it (e.g. push a phone notification when a drone enters a HA zone you've drawn around your property).

---

## 10. Updating the integration

When a new release ships:

1. HACS -> **WarDragon** -> **Redownload** if the version doesn't auto-update.
2. **Restart Home Assistant**.
3. Hard-refresh your browser (Ctrl-Shift-R) once so any updated COP card bundle gets pulled.

---

## Where to go next

- [DASHBOARDS.md](DASHBOARDS.md) — alternative dashboard layouts (tabbed, panel/wallboard) if the default side-by-side isn't what you want.
- README **Architecture** section — internals if you want to contribute or extend.
- README **Troubleshooting** section — common problems and the fixes.
