import type { Drone, HomeAssistant, Kit, SignalEvent } from "../types";

const DRONE_TRACKER_PREFIX = "device_tracker.drone_";
const KIT_TRACKER_PREFIX = "device_tracker.wardragon_";

function asNumber(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function asString(v: unknown): string | null {
  if (typeof v === "string") {
    const s = v.trim();
    return s ? s : null;
  }
  return null;
}

function isMainDroneTracker(entityId: string): boolean {
  if (!entityId.startsWith(DRONE_TRACKER_PREFIX)) return false;
  if (!entityId.endsWith("_position")) return false;
  if (entityId.endsWith("_pilot_position")) return false;
  if (entityId.endsWith("_home_position")) return false;
  return true;
}

function isMainKitTracker(entityId: string): boolean {
  if (!entityId.startsWith(KIT_TRACKER_PREFIX)) return false;
  if (!entityId.endsWith("_position")) return false;
  if (entityId.endsWith("_signal_position")) return false;
  if (entityId.endsWith("_signal_signal_position")) return false;
  return true;
}

export function findDrones(hass: HomeAssistant): Drone[] {
  const out: Drone[] = [];
  for (const entityId of Object.keys(hass.states)) {
    if (!isMainDroneTracker(entityId)) continue;
    const s = hass.states[entityId];
    const a = s.attributes;
    const callsign =
      asString(a.description) ?? entityId.replace(DRONE_TRACKER_PREFIX, "").replace(/_position$/, "");
    out.push({
      entityId,
      callsign,
      description: asString(a.description),
      rssi: asNumber(a.rssi),
      protocolFamily: asString(a.protocol_family),
      droneClass: asString(a.drone_class),
      freqBand: asString(a.freq_band),
      freqMhz: asNumber(a.freq_mhz),
      online: s.state !== "unavailable" && s.state !== "unknown",
      seenBy: asString(a.seen_by),
      kitCount: asNumber(a.kit_count) ?? 1,
      hasPosition: asNumber(a.latitude) !== null && asNumber(a.longitude) !== null,
      latitude: asNumber(a.latitude),
      longitude: asNumber(a.longitude),
      altitude: asNumber(a.altitude),
      speed: asNumber(a.speed),
      direction: asNumber(a.direction),
      uaType: asString(a.ua_type_name),
      operatorId: asString(a.operator_id),
      caaId: asString(a.caa_id),
      ridMake: asString(a.rid_make),
      ridModel: asString(a.rid_model),
      lastChanged: new Date(s.last_changed),
    });
  }
  return out;
}

export function findKits(hass: HomeAssistant): Kit[] {
  const out: Kit[] = [];
  for (const entityId of Object.keys(hass.states)) {
    if (!isMainKitTracker(entityId)) continue;
    const s = hass.states[entityId];
    const a = s.attributes;
    const baseSlug = entityId
      .replace(KIT_TRACKER_PREFIX, "")
      .replace(/_position$/, "");
    const kitId = `wardragon-${baseSlug.toUpperCase().replace(/_/g, "")}`;
    const sensorBase = `sensor.wardragon_${baseSlug}`;
    const binBase = `binary_sensor.wardragon_${baseSlug}`;
    const cpu = asNumber(hass.states[`${sensorBase}_cpu_usage`]?.state);
    const temperatureC = asNumber(hass.states[`${sensorBase}_temperature_c`]?.state);
    const plutoTempC = asNumber(hass.states[`${sensorBase}_pluto_temp_c`]?.state);
    const zynqTempC = asNumber(hass.states[`${sensorBase}_zynq_temp_c`]?.state);
    const uptimeS = asNumber(hass.states[`${sensorBase}_uptime_s`]?.state);
    const onlineBin = hass.states[`${binBase}_online`];
    const gpsFixBin = hass.states[`${binBase}_gps_fix`];
    out.push({
      kitId,
      positionEntityId: entityId,
      online: onlineBin ? onlineBin.state === "on" : s.state !== "unavailable",
      gpsFix: gpsFixBin ? gpsFixBin.state === "on" : false,
      cpuUsage: cpu,
      temperatureC,
      plutoTempC,
      zynqTempC,
      uptimeS,
      hasPosition: asNumber(a.latitude) !== null && asNumber(a.longitude) !== null,
      latitude: asNumber(a.latitude),
      longitude: asNumber(a.longitude),
      lastChanged: new Date(s.last_changed),
    });
  }
  return out;
}

export function findSignals(hass: HomeAssistant): SignalEvent[] {
  // Per-kit current signal sensors look like sensor.wardragon_<slug>_signal_type, etc.
  const kits = new Map<string, string>(); // kitId → sensor base
  for (const entityId of Object.keys(hass.states)) {
    const m = entityId.match(/^sensor\.(wardragon_[^_]+(?:_[^_]+)*)_signal_type$/);
    if (!m) continue;
    const base = m[1];
    const kitId = `wardragon-${base.replace("wardragon_", "").toUpperCase().replace(/_/g, "")}`;
    if (!kits.has(kitId)) kits.set(kitId, `sensor.${base}`);
  }
  const out: SignalEvent[] = [];
  for (const [kitId, base] of kits) {
    const typeS = hass.states[`${base}_signal_type`];
    if (!typeS || typeS.state === "unavailable" || typeS.state === "unknown") continue;
    out.push({
      kitId,
      signalType: asString(typeS.state),
      source: asString(hass.states[`${base}_signal_source`]?.state),
      callsign: asString(hass.states[`${base}_signal_callsign`]?.state),
      rssi: asNumber(hass.states[`${base}_signal_rssi`]?.state),
      centerMhz: asNumber(hass.states[`${base}_signal_center_mhz`]?.state),
      bandwidthMhz: asNumber(hass.states[`${base}_signal_bandwidth_mhz`]?.state),
      lastChanged: new Date(typeS.last_changed),
    });
  }
  return out;
}

export function fmtAge(d: Date, now: Date = new Date()): string {
  const ms = now.getTime() - d.getTime();
  const s = Math.max(0, Math.floor(ms / 1000));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  const days = Math.floor(h / 24);
  return `${days}d`;
}

export function fmtUptime(seconds: number | null): string {
  if (seconds === null) return "—";
  const s = Math.max(0, Math.floor(seconds));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  const days = Math.floor(h / 24);
  const remH = h % 24;
  return `${days}d ${remH}h`;
}

export function fmtNum(n: number | null, digits: number = 1, suffix: string = ""): string {
  if (n === null) return "—";
  return `${n.toFixed(digits)}${suffix}`;
}
