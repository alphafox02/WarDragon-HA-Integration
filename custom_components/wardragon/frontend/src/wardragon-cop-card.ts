/**
 * WarDragon Common Operating Picture (COP) — bundled Lovelace card.
 *
 * Renders a tactical operator console: stat header, searchable / filterable /
 * sortable drone roster, per-kit health panel, recent FPV/RF signal feed.
 *
 * Designed for HA users coming from ATAK/TAK: dense info, dark-friendly,
 * subdued accent colours, monospace values, no flashy emojis or AI-style
 * over-the-top surveillance vibes.
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

const VERSION = "0.2.0";
const CARD_TYPE = "wardragon-cop-card";

const KNOWN_PROTOCOLS = [
  "O2",
  "O3",
  "O4",
  "OcuSync",
  "WiFi-Beacon",
  "WiFi-NaN",
  "BT5-LR",
  "ISM-FHSS",
];
const KNOWN_BANDS = ["900MHz", "2.4GHz", "5.2GHz", "5.8GHz"];

export class WarDragonCopCard extends LitElement {
  @property({ attribute: false }) hass?: HomeAssistant;

  @state() private _config?: CopCardConfig;
  @state() private _query = "";
  @state() private _selectedProtocols = new Set<string>();
  @state() private _selectedBands = new Set<string>();
  @state() private _onlineOnly = false;
  @state() private _sort: SortKey = "last_seen";
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
    if (config.default_filter?.protocols) {
      this._selectedProtocols = new Set(config.default_filter.protocols);
    }
    if (config.default_filter?.bands) {
      this._selectedBands = new Set(config.default_filter.bands);
    }
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
      // Recompute a rough count by examining each kit's signal_type sensor's
      // last_changed timestamp. Not a real time-series, but operationally
      // useful as "how many distinct kit signal updates in the last hour".
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
    const filtered = this._applyFilters(drones);
    const sorted = this._applySort(filtered);
    const onlineCount = drones.filter((d) => d.online).length;
    const onlineKits = kits.filter((k) => k.online).length;

    return html`
      <ha-card>
        <div class="cop-header">
          <div class="cop-titlebar">
            <div class="cop-title">${this._config?.title ?? "WarDragon COP"}</div>
            <div class="stat-sub" title="Common Operating Picture">v${VERSION}</div>
          </div>
          <div class="cop-stats">
            <div class="stat-tile">
              <div class="stat-label">Tracks</div>
              <div class="stat-value">${onlineCount}</div>
              <div class="stat-sub">${drones.length} total / ${filtered.length} shown</div>
            </div>
            <div class="stat-tile">
              <div class="stat-label">Kits</div>
              <div class="stat-value">${onlineKits}</div>
              <div class="stat-sub">${kits.length} total</div>
            </div>
            <div class="stat-tile">
              <div class="stat-label">Signals (1h)</div>
              <div class="stat-value">${this._signalsLastHour}</div>
              <div class="stat-sub">${signals.length} active kits</div>
            </div>
          </div>
          <div class="cop-controls">
            <input
              class="cop-search"
              type="search"
              placeholder="Search ID / description / operator / seen-by"
              .value=${this._query}
              @input=${(e: InputEvent) => (this._query = (e.target as HTMLInputElement).value)}
            />
            <select
              class="cop-sort"
              .value=${this._sort}
              @change=${(e: Event) => (this._sort = (e.target as HTMLSelectElement).value as SortKey)}
            >
              <option value="last_seen">Sort: Last seen</option>
              <option value="rssi">Sort: RSSI (strongest)</option>
              <option value="altitude">Sort: Altitude</option>
              <option value="speed">Sort: Speed</option>
              <option value="callsign">Sort: Callsign</option>
            </select>
          </div>
          <div class="cop-chips">
            <span
              class="chip"
              data-active=${String(this._onlineOnly)}
              @click=${() => (this._onlineOnly = !this._onlineOnly)}
              >online only</span
            >
            ${KNOWN_BANDS.map(
              (b) => html`<span
                class="chip"
                data-active=${String(this._selectedBands.has(b))}
                @click=${() => this._toggleBand(b)}
                >${b}</span
              >`,
            )}
            ${KNOWN_PROTOCOLS.map(
              (p) => html`<span
                class="chip"
                data-active=${String(this._selectedProtocols.has(p))}
                @click=${() => this._toggleProtocol(p)}
                >${p}</span
              >`,
            )}
          </div>
        </div>

        <div class="cop-section">
          <div class="section-title">
            <span>Drone Roster</span>
            <span class="section-count">${sorted.length}</span>
          </div>
          ${sorted.length === 0
            ? html`<div class="empty-state">No drones match the current filters.</div>`
            : html`<div class="roster">${sorted.map((d) => this._renderDrone(d))}</div>`}
        </div>

        <div class="cop-section">
          <div class="section-title">
            <span>Kits</span>
            <span class="section-count">${kits.length}</span>
          </div>
          ${kits.length === 0
            ? html`<div class="empty-state">No WarDragon kits have reported yet.</div>`
            : html`<div class="kit-grid">${kits.map((k) => this._renderKit(k))}</div>`}
        </div>

        <div class="cop-section">
          <div class="section-title">
            <span>Recent Signals</span>
            <span class="section-count">${signals.length}</span>
          </div>
          ${signals.length === 0
            ? html`<div class="empty-state">No FPV/RF signal channels active.</div>`
            : signals.map((s) => this._renderSignal(s))}
        </div>
      </ha-card>
    `;
  }

  // ---------- helpers ----------

  private _toggleBand(b: string): void {
    const next = new Set(this._selectedBands);
    next.has(b) ? next.delete(b) : next.add(b);
    this._selectedBands = next;
  }

  private _toggleProtocol(p: string): void {
    const next = new Set(this._selectedProtocols);
    next.has(p) ? next.delete(p) : next.add(p);
    this._selectedProtocols = next;
  }

  private _applyFilters(drones: Drone[]): Drone[] {
    const q = this._query.trim().toLowerCase();
    return drones.filter((d) => {
      if (this._onlineOnly && !d.online) return false;
      if (this._selectedBands.size > 0 && (!d.freqBand || !this._selectedBands.has(d.freqBand)))
        return false;
      if (
        this._selectedProtocols.size > 0 &&
        (!d.protocolFamily || !this._selectedProtocols.has(d.protocolFamily))
      )
        return false;
      if (q) {
        const hay = [
          d.callsign,
          d.description ?? "",
          d.seenBy ?? "",
          d.operatorId ?? "",
          d.caaId ?? "",
          d.entityId,
        ]
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  private _applySort(drones: Drone[]): Drone[] {
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

  private _renderDrone(d: Drone): TemplateResult {
    const state = d.online ? "online" : "offline";
    return html`
      <div class="drone-row">
        <div class="drone-status" data-state=${state}></div>
        <div class="drone-main" @click=${() => this._showMoreInfo(d.entityId)}>
          <div class="drone-callsign">${d.callsign}</div>
          <div class="drone-meta">
            ${d.protocolFamily ? html`<span class="tag">${d.protocolFamily}</span>` : ""}
            ${d.freqBand
              ? html`<span class="tag" data-band=${d.freqBand}>${d.freqBand}</span>`
              : ""}
            ${d.rssi !== null ? html`<span>RSSI ${fmtNum(d.rssi, 0, " dBm")}</span>` : ""}
            ${d.altitude !== null ? html`<span>ALT ${fmtNum(d.altitude, 0, " m")}</span>` : ""}
            ${d.speed !== null ? html`<span>SPD ${fmtNum(d.speed, 1, " m/s")}</span>` : ""}
            ${d.kitCount > 1 ? html`<span class="tag">×${d.kitCount} kits</span>` : ""}
            <span>${fmtAge(d.lastChanged)}</span>
            ${d.seenBy ? html`<span>seen-by ${d.seenBy}</span>` : ""}
          </div>
        </div>
        <div class="drone-actions">
          <button title="View history" @click=${() => this._showMoreInfo(d.entityId)}>info</button>
          <button data-danger title="Clear drone" @click=${() => this._clearDrone(d)}>×</button>
        </div>
      </div>
    `;
  }

  private _renderKit(k: Kit): TemplateResult {
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

  private _renderSignal(s: SignalEvent): TemplateResult {
    const meta = [
      s.callsign ? `"${s.callsign}"` : "",
      s.centerMhz !== null ? `${fmtNum(s.centerMhz, 1, " MHz")}` : "",
      s.bandwidthMhz !== null ? `BW ${fmtNum(s.bandwidthMhz, 1, " MHz")}` : "",
      s.source ? `via ${s.source}` : "",
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

  private _showMoreInfo(entityId: string): void {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private async _clearDrone(d: Drone): Promise<void> {
    if (!this.hass) return;
    // entityId is e.g. device_tracker.drone_f6q8d244c00cl2kf_position; the
    // service expects the actual drone_id (e.g. drone-F6Q8D244C00CL2KF).
    // We round-trip via the entity's serial_number on the device, but
    // since we don't have the device registry handy here, use callsign as
    // a fallback hint and rely on the user pulling the exact ID from the
    // entity's more-info dialog. For drones with description set, prompt.
    const idGuess = prompt(
      `Clear drone — enter exact drone_id (case-sensitive).\n\nHint: ${d.callsign}`,
      "",
    );
    if (!idGuess) return;
    try {
      await this.hass.callService("wardragon", "clear_drone", { drone_id: idGuess.trim() });
    } catch (e) {
      console.error("[WarDragon COP] clear_drone failed", e);
    }
  }
}

// Register against the global registry explicitly. We avoid Lit's
// @customElement decorator because, when this bundle is evaluated under
// HA's @webcomponents/scoped-custom-element-registry polyfill, decorator-
// time `customElements.define` calls can be routed to a scoped registry
// rather than the global one — leaving HA's lovelace card lookup unable
// to find the element. Loading the bundle via a classic <script> tag
// (frontend.py: es5=True) plus this explicit global define is the
// belt-and-suspenders fix.
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
