/**
 * WarDragon Common Operating Picture (COP) — bundled Lovelace card.
 *
 * Tactical operator console for HA users coming from ATAK / TAK. Layout:
 *
 *   ┌── Header ──────────────────────────────────┐
 *   │ WARDRAGON COP                              │
 *   │ Stats strip: tracks / kits / signals(1h)   │
 *   │ Search + Sort + Online-only                │
 *   ├── Tab bar: [Drones] [Kits] [Signals] ──────┤
 *   │                                            │
 *   │   active tab content (scrollable)          │
 *   │                                            │
 *   └────────────────────────────────────────────┘
 *
 * Drones tab is the default — a scrollable, searchable, sortable roster
 * sorted most-recent-first by default (matching the WarDragon ATAK app
 * mental model). Kits tab gives per-kit health cards for operators who
 * want all kits at once; click a kit on the HA map for the same data via
 * the native more-info dialog. Signals tab shows the latest FPV/RF
 * detection per kit.
 *
 * Element registration is explicit (no Lit @customElement decorator) so
 * the bundle stays compatible with HA's scoped-custom-element-registry
 * polyfill — see project_cop_card_registration.md.
 */

import { LitElement, html, css, type CSSResult, type TemplateResult, type PropertyValues } from "lit";
import { property, state } from "lit/decorators.js";

import type {
  CopCardConfig,
  Drone,
  HomeAssistant,
  Kit,
  SignalEvent,
  SortKey,
} from "./types";
import {
  findDrones,
  findKits,
  findSignals,
  fmtAge,
  fmtNum,
  fmtUptime,
} from "./utils/ha-helpers";
import { copTheme } from "./styles/theme";

const VERSION = "0.3.0";
const CARD_TYPE = "wardragon-cop-card";
type Tab = "drones" | "kits" | "signals";

export class WarDragonCopCard extends LitElement {
  @property({ attribute: false }) hass?: HomeAssistant;

  @state() private _config?: CopCardConfig;
  @state() private _query = "";
  @state() private _onlineOnly = false;
  @state() private _sort: SortKey = "last_seen";
  @state() private _tab: Tab = "drones";
  @state() private _signalsLastHour = 0;

  private _signalCounter: { count: number; resetAt: number } = { count: 0, resetAt: 0 };

  static get styles(): CSSResult {
    return copTheme;
  }

  setConfig(config: CopCardConfig): void {
    if (!config) {
      throw new Error("WarDragon COP card: missing config");
    }
    this._config = config;
    if (config.default_filter?.online_only) this._onlineOnly = true;
  }

  getCardSize(): number {
    return 8;
  }

  static getStubConfig(): CopCardConfig {
    return { type: `custom:${CARD_TYPE}` };
  }

  protected willUpdate(changed: PropertyValues): void {
    if (changed.has("hass") && this.hass) {
      this._refreshSignalsLastHour();
    }
  }

  private _refreshSignalsLastHour(): void {
    if (!this.hass) return;
    const now = Date.now();
    if (now - this._signalCounter.resetAt > 60_000) {
      let count = 0;
      const cutoff = now - 60 * 60 * 1000;
      for (const sig of findSignals(this.hass)) {
        if (sig.lastChanged.getTime() >= cutoff) count++;
      }
      this._signalsLastHour = count;
      this._signalCounter = { count, resetAt: now };
    }
  }

  protected render(): TemplateResult {
    if (!this.hass) {
      return html`<ha-card><div class="empty-state">Loading…</div></ha-card>`;
    }
    const drones = findDrones(this.hass);
    const kits = findKits(this.hass);
    const signals = findSignals(this.hass);
    const onlineDrones = drones.filter((d) => d.online).length;
    const onlineKits = kits.filter((k) => k.online).length;

    return html`
      <ha-card>
        <div class="cop-header">
          <div class="cop-titlebar">
            <div class="cop-title">${this._config?.title ?? "WarDragon COP"}</div>
            <div class="cop-version" title=${`Common Operating Picture v${VERSION}`}>v${VERSION}</div>
          </div>
          <div class="cop-stats">
            <div class="stat-tile">
              <div class="stat-label">Tracks</div>
              <div class="stat-value">${onlineDrones}</div>
              <div class="stat-sub">${drones.length} total</div>
            </div>
            <div class="stat-tile">
              <div class="stat-label">Kits</div>
              <div class="stat-value">${onlineKits}</div>
              <div class="stat-sub">${kits.length} total</div>
            </div>
            <div class="stat-tile">
              <div class="stat-label">Signals (1h)</div>
              <div class="stat-value">${this._signalsLastHour}</div>
              <div class="stat-sub">${signals.length} active</div>
            </div>
          </div>
          <div class="cop-controls">
            <input
              class="cop-search"
              type="search"
              placeholder=${this._tab === "drones"
                ? "Search ID / description / operator / kit"
                : this._tab === "kits"
                ? "Search kit ID"
                : "Search signal type / callsign"}
              .value=${this._query}
              @input=${(e: InputEvent) => (this._query = (e.target as HTMLInputElement).value)}
            />
            ${this._tab === "drones"
              ? html`<select
                  class="cop-sort"
                  .value=${this._sort}
                  @change=${(e: Event) => (this._sort = (e.target as HTMLSelectElement).value as SortKey)}
                >
                  <option value="last_seen">Last seen</option>
                  <option value="rssi">RSSI (strongest)</option>
                  <option value="altitude">Altitude</option>
                  <option value="speed">Speed</option>
                  <option value="callsign">Callsign</option>
                </select>`
              : ""}
            <label class="cop-toggle">
              <input
                type="checkbox"
                .checked=${this._onlineOnly}
                @change=${(e: Event) => (this._onlineOnly = (e.target as HTMLInputElement).checked)}
              />
              <span>Online only</span>
            </label>
          </div>
        </div>

        <div class="cop-tabs" role="tablist">
          ${this._renderTab("drones", "Drones", drones.length)}
          ${this._renderTab("kits", "Kits", kits.length)}
          ${this._renderTab("signals", "Signals", signals.length)}
        </div>

        <div class="cop-tab-content">
          ${this._tab === "drones" ? this._renderDronesTab(drones) : ""}
          ${this._tab === "kits" ? this._renderKitsTab(kits) : ""}
          ${this._tab === "signals" ? this._renderSignalsTab(signals) : ""}
        </div>
      </ha-card>
    `;
  }

  // ---------- tab bar ----------

  private _renderTab(id: Tab, label: string, count: number): TemplateResult {
    const active = this._tab === id;
    return html`
      <button
        role="tab"
        aria-selected=${active}
        class="cop-tab"
        data-active=${String(active)}
        @click=${() => (this._tab = id)}
      >
        <span class="tab-label">${label}</span>
        <span class="tab-count">${count}</span>
      </button>
    `;
  }

  // ---------- drones tab ----------

  private _renderDronesTab(drones: Drone[]): TemplateResult {
    const filtered = this._filterDrones(drones);
    const sorted = this._sortDrones(filtered);
    if (sorted.length === 0) {
      return html`<div class="empty-state">${
        drones.length === 0 ? "No drones detected." : "No drones match the current filter."
      }</div>`;
    }
    return html`<div class="roster">${sorted.map((d) => this._renderDroneRow(d))}</div>`;
  }

  private _filterDrones(drones: Drone[]): Drone[] {
    const q = this._query.trim().toLowerCase();
    return drones.filter((d) => {
      if (this._onlineOnly && !d.online) return false;
      if (q) {
        const hay = [
          d.callsign,
          d.description ?? "",
          d.seenBy ?? "",
          d.operatorId ?? "",
          d.caaId ?? "",
          d.protocolFamily ?? "",
          d.freqBand ?? "",
          d.entityId,
        ]
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  private _sortDrones(drones: Drone[]): Drone[] {
    const arr = [...drones];
    switch (this._sort) {
      case "rssi":
        arr.sort((a, b) => (b.rssi ?? -Infinity) - (a.rssi ?? -Infinity));
        break;
      case "altitude":
        arr.sort((a, b) => (b.altitude ?? -Infinity) - (a.altitude ?? -Infinity));
        break;
      case "speed":
        arr.sort((a, b) => (b.speed ?? -Infinity) - (a.speed ?? -Infinity));
        break;
      case "callsign":
        arr.sort((a, b) => a.callsign.localeCompare(b.callsign));
        break;
      case "last_seen":
      default:
        arr.sort((a, b) => b.lastChanged.getTime() - a.lastChanged.getTime());
    }
    return arr;
  }

  private _renderDroneRow(d: Drone): TemplateResult {
    const state = d.online ? "online" : "offline";
    return html`
      <div class="drone-row" @click=${() => this._showMoreInfo(d.entityId)}>
        <div class="drone-status" data-state=${state}></div>
        <div class="drone-main">
          <div class="drone-callsign">${d.callsign}</div>
          <div class="drone-meta">
            ${d.protocolFamily ? html`<span class="tag">${d.protocolFamily}</span>` : ""}
            ${d.freqBand
              ? html`<span class="tag" data-band=${d.freqBand}>${d.freqBand}</span>`
              : ""}
            ${d.rssi !== null ? html`<span>${fmtNum(d.rssi, 0, " dBm")}</span>` : ""}
            ${d.altitude !== null ? html`<span>${fmtNum(d.altitude, 0, " m")}</span>` : ""}
            ${d.speed !== null ? html`<span>${fmtNum(d.speed, 1, " m/s")}</span>` : ""}
            ${d.kitCount > 1 ? html`<span class="tag">×${d.kitCount} kits</span>` : ""}
            <span class="age">${fmtAge(d.lastChanged)}</span>
            ${d.seenBy ? html`<span class="seen-by">by ${d.seenBy}</span>` : ""}
          </div>
        </div>
      </div>
    `;
  }

  // ---------- kits tab ----------

  private _renderKitsTab(kits: Kit[]): TemplateResult {
    const q = this._query.trim().toLowerCase();
    const filtered = kits.filter((k) => {
      if (this._onlineOnly && !k.online) return false;
      if (q && !k.kitId.toLowerCase().includes(q)) return false;
      return true;
    });
    if (filtered.length === 0) {
      return html`<div class="empty-state">${
        kits.length === 0 ? "No WarDragon kits have reported yet." : "No kits match the filter."
      }</div>`;
    }
    return html`<div class="kit-grid">${filtered.map((k) => this._renderKitCard(k))}</div>`;
  }

  private _renderKitCard(k: Kit): TemplateResult {
    return html`
      <div class="kit-card" @click=${() => this._showMoreInfo(k.positionEntityId)}>
        <div class="kit-id">${k.kitId}</div>
        <div class="kit-name">
          WarDragon
          <span class="pill" data-state=${k.online ? "online" : "offline"}>
            ${k.online ? "online" : "offline"}
          </span>
          ${k.gpsFix ? html`<span class="pill" data-state="online">gps fix</span>` : ""}
        </div>
        <div class="kit-stats">
          <span>CPU</span><span class="v">${fmtNum(k.cpuUsage, 1, "%")}</span>
          <span>Temp</span><span class="v">${fmtNum(k.temperatureC, 1, "°C")}</span>
          <span>Pluto</span><span class="v">${fmtNum(k.plutoTempC, 1, "°C")}</span>
          <span>Zynq</span><span class="v">${fmtNum(k.zynqTempC, 1, "°C")}</span>
          <span>Up</span><span class="v">${fmtUptime(k.uptimeS)}</span>
        </div>
      </div>
    `;
  }

  // ---------- signals tab ----------

  private _renderSignalsTab(signals: SignalEvent[]): TemplateResult {
    const q = this._query.trim().toLowerCase();
    const filtered = signals.filter((s) => {
      if (q) {
        const hay = `${s.signalType ?? ""} ${s.callsign ?? ""} ${s.source ?? ""} ${s.kitId}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    if (filtered.length === 0) {
      return html`<div class="empty-state">${
        signals.length === 0
          ? "No FPV/RF signal channels active. Enable mqtt_signals in DragonSync to populate."
          : "No signals match the filter."
      }</div>`;
    }
    const sorted = [...filtered].sort((a, b) => b.lastChanged.getTime() - a.lastChanged.getTime());
    return html`<div class="signal-list">${sorted.map((s) => this._renderSignalRow(s))}</div>`;
  }

  private _renderSignalRow(s: SignalEvent): TemplateResult {
    const meta = [
      s.callsign ? `"${s.callsign}"` : "",
      s.centerMhz !== null ? fmtNum(s.centerMhz, 1, " MHz") : "",
      s.bandwidthMhz !== null ? `BW ${fmtNum(s.bandwidthMhz, 1, " MHz")}` : "",
      s.source ? `via ${s.source}` : "",
      s.kitId,
      `${fmtAge(s.lastChanged)} ago`,
    ]
      .filter(Boolean)
      .join("  ·  ");
    return html`
      <div class="signal-row">
        <span class="signal-type">${s.signalType ?? "—"}</span>
        <span class="signal-meta">${meta}</span>
        <span class="signal-rssi">${fmtNum(s.rssi, 0, " dBm")}</span>
      </div>
    `;
  }

  // ---------- helpers ----------

  private _showMoreInfo(entityId: string): void {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      }),
    );
  }
}

// Explicit registration against the global registry. We intentionally avoid
// Lit's @customElement decorator so the bundled scoped-custom-element-
// registry polyfill (loaded inside HA) can't route the registration to a
// scoped registry — HA's lovelace card lookup queries the global one.
if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, WarDragonCopCard);
}

if (!window.customCards) window.customCards = [];
if (!window.customCards.find((c) => c.type === CARD_TYPE)) {
  window.customCards.push({
    type: CARD_TYPE,
    name: "WarDragon COP",
    description: "Common Operating Picture for WarDragon detection kits",
    preview: false,
  });
}
