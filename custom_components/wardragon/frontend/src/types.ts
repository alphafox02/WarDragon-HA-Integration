// Lightweight HA frontend type shims. We avoid the `custom-card-helpers`
// dep so the build stays self-contained and version-independent.

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
}

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  language: string;
  themes?: Record<string, unknown>;
  callService: (
    domain: string,
    service: string,
    data?: Record<string, unknown>,
  ) => Promise<void>;
}

export interface LovelaceCardConfig {
  type: string;
  [key: string]: unknown;
}

export interface CopCardConfig extends LovelaceCardConfig {
  type: string;
  title?: string;
  default_filter?: {
    online_only?: boolean;
    bands?: string[];
    protocols?: string[];
  };
}

export interface Drone {
  entityId: string;
  callsign: string;
  description: string | null;
  rssi: number | null;
  protocolFamily: string | null;
  freqBand: string | null;
  freqMhz: number | null;
  online: boolean;
  seenBy: string | null;
  kitCount: number;
  hasPosition: boolean;
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  speed: number | null;
  direction: number | null;
  uaType: string | null;
  operatorId: string | null;
  caaId: string | null;
  ridMake: string | null;
  ridModel: string | null;
  lastChanged: Date;
}

export interface Kit {
  kitId: string;
  positionEntityId: string;
  online: boolean;
  gpsFix: boolean;
  cpuUsage: number | null;
  temperatureC: number | null;
  plutoTempC: number | null;
  zynqTempC: number | null;
  uptimeS: number | null;
  hasPosition: boolean;
  latitude: number | null;
  longitude: number | null;
  lastChanged: Date;
}

export interface SignalEvent {
  kitId: string;
  signalType: string | null;
  source: string | null;
  callsign: string | null;
  rssi: number | null;
  centerMhz: number | null;
  bandwidthMhz: number | null;
  lastChanged: Date;
}

export type SortKey =
  | "callsign"
  | "rssi"
  | "altitude"
  | "speed"
  | "last_seen";

declare global {
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description?: string;
      preview?: boolean;
    }>;
  }
}
