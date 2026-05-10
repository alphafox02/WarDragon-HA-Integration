import { css, type CSSResult } from "lit";

// Tactical, professional, theme-aware. Pulls from HA's CSS variables so
// the card matches both light and dark dashboards. Subdued accent
// (cyan-blue) mirrors the WarDragon dragon mark; status uses a small
// fixed palette rather than rainbow chips. Tabs follow ATAK-app feel.

export const copTheme: CSSResult = css`
  :host {
    --wd-bg: var(--card-background-color, #1c1f24);
    --wd-bg-soft: var(--ha-card-background, var(--wd-bg));
    --wd-bg-row: color-mix(in srgb, var(--wd-bg) 92%, transparent);
    --wd-bg-row-alt: color-mix(in srgb, var(--wd-bg) 96%, transparent);
    --wd-text: var(--primary-text-color, #e0e0e0);
    --wd-text-muted: var(--secondary-text-color, #a0a0a0);
    --wd-divider: var(--divider-color, rgba(255, 255, 255, 0.1));
    --wd-accent: #4aa3ff;
    --wd-accent-soft: rgba(74, 163, 255, 0.12);
    --wd-ok: #4caf50;
    --wd-warn: #ff9800;
    --wd-alert: #f44336;
    --wd-mute: #6e7480;
    --wd-mono: var(--code-font-family, ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace);

    display: block;
    color: var(--wd-text);
    font-family: var(--paper-font-body1_-_font-family, var(--mdc-typography-body2-font-family, "Roboto", sans-serif));
  }

  ha-card {
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* ---- header ---- */

  .cop-header {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 14px 16px 12px;
    border-bottom: 1px solid var(--wd-divider);
  }

  .cop-titlebar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .cop-title {
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .cop-title::before {
    content: "";
    width: 6px;
    height: 18px;
    background: var(--wd-accent);
    border-radius: 1px;
  }
  .cop-version {
    font-size: 0.7rem;
    color: var(--wd-text-muted);
    font-family: var(--wd-mono);
  }

  .cop-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  .stat-tile {
    background: var(--wd-bg-row);
    border-radius: 6px;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    border: 1px solid var(--wd-divider);
  }
  .stat-label {
    font-size: 0.7rem;
    color: var(--wd-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .stat-value {
    font-size: 1.4rem;
    font-weight: 600;
    font-family: var(--wd-mono);
    line-height: 1.1;
  }
  .stat-sub {
    font-size: 0.7rem;
    color: var(--wd-text-muted);
    font-family: var(--wd-mono);
  }

  .cop-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .cop-search {
    flex: 1 1 200px;
    min-width: 140px;
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    color: var(--wd-text);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 0.9rem;
    outline: none;
  }
  .cop-search:focus {
    border-color: var(--wd-accent);
    box-shadow: 0 0 0 1px var(--wd-accent-soft);
  }
  .cop-sort {
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    color: var(--wd-text);
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 0.8rem;
  }
  .cop-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8rem;
    color: var(--wd-text-muted);
    cursor: pointer;
    user-select: none;
  }
  .cop-toggle input {
    accent-color: var(--wd-accent);
    cursor: pointer;
  }

  /* ---- tab bar ---- */

  .cop-tabs {
    display: flex;
    background: var(--wd-bg-row-alt);
    border-bottom: 1px solid var(--wd-divider);
  }
  .cop-tab {
    flex: 1 1 0;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    color: var(--wd-text-muted);
    padding: 10px 12px;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: color 0.1s, border-color 0.1s, background 0.1s;
  }
  .cop-tab:hover {
    color: var(--wd-text);
    background: var(--wd-bg-row);
  }
  .cop-tab[data-active="true"] {
    color: var(--wd-accent);
    border-bottom-color: var(--wd-accent);
    background: var(--wd-bg);
  }
  .tab-count {
    font-family: var(--wd-mono);
    font-size: 0.7rem;
    color: var(--wd-text-muted);
    background: var(--wd-bg);
    padding: 1px 6px;
    border-radius: 10px;
    border: 1px solid var(--wd-divider);
    min-width: 18px;
    text-align: center;
  }
  .cop-tab[data-active="true"] .tab-count {
    color: var(--wd-accent);
    border-color: var(--wd-accent);
  }

  /* ---- tab content ---- */

  .cop-tab-content {
    flex: 1 1 auto;
    overflow-y: auto;
    max-height: 540px;
  }
  .empty-state {
    padding: 24px 16px;
    color: var(--wd-text-muted);
    font-style: italic;
    font-size: 0.85rem;
    text-align: center;
  }

  /* ---- drone-class chips ---- */

  .class-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--wd-divider);
    background: var(--wd-bg-row-alt);
  }
  .class-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--wd-bg);
    border: 1px solid var(--wd-divider);
    color: var(--wd-text-muted);
    padding: 4px 10px;
    font-size: 0.75rem;
    border-radius: 999px;
    cursor: pointer;
    user-select: none;
    font-family: inherit;
    transition: background 0.1s, color 0.1s, border-color 0.1s;
  }
  .class-chip:hover {
    color: var(--wd-text);
  }
  .class-chip[data-active="true"] {
    background: var(--wd-accent-soft);
    color: var(--wd-accent);
    border-color: var(--wd-accent);
  }
  .class-chip-count {
    font-family: var(--wd-mono);
    font-size: 0.7rem;
    background: var(--wd-bg-row);
    padding: 0 6px;
    border-radius: 999px;
    color: var(--wd-text-muted);
    border: 1px solid var(--wd-divider);
  }
  .class-chip[data-active="true"] .class-chip-count {
    color: var(--wd-accent);
    border-color: var(--wd-accent);
  }
  .class-chip[data-class="DJI"][data-active="true"]      { color: #ffb84d; border-color: #ffb84d; background: rgba(255, 184, 77, 0.12); }
  .class-chip[data-class="DJI"][data-active="true"] .class-chip-count { color: #ffb84d; border-color: #ffb84d; }
  .class-chip[data-class="Open RID"][data-active="true"] { color: #4dd0e1; border-color: #4dd0e1; background: rgba(77, 208, 225, 0.12); }
  .class-chip[data-class="Open RID"][data-active="true"] .class-chip-count { color: #4dd0e1; border-color: #4dd0e1; }
  .class-chip[data-class="FPV"][data-active="true"]      { color: #f06292; border-color: #f06292; background: rgba(240, 98, 146, 0.12); }
  .class-chip[data-class="FPV"][data-active="true"] .class-chip-count { color: #f06292; border-color: #f06292; }
  .class-chip[data-class="Other"][data-active="true"]    { color: var(--wd-text); border-color: var(--wd-text); background: var(--wd-bg-row); }
  .class-chip[data-class="Other"][data-active="true"] .class-chip-count { color: var(--wd-text); border-color: var(--wd-text); }

  /* ---- drone roster ---- */

  .roster {
    display: flex;
    flex-direction: column;
  }
  .drone-row {
    display: grid;
    grid-template-columns: 12px 1fr;
    gap: 10px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--wd-divider);
    align-items: center;
    cursor: pointer;
    transition: background 0.1s;
  }
  .drone-row:nth-child(even) {
    background: var(--wd-bg-row-alt);
  }
  .drone-row:hover {
    background: var(--wd-accent-soft);
  }
  .drone-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--wd-mute);
  }
  .drone-status[data-state="online"] {
    background: var(--wd-ok);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.18);
  }

  .drone-main {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }
  .drone-callsign {
    font-weight: 600;
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .drone-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 10px;
    font-size: 0.74rem;
    color: var(--wd-text-muted);
    font-family: var(--wd-mono);
    align-items: center;
  }
  .drone-meta .tag {
    background: var(--wd-bg-row);
    color: var(--wd-text);
    padding: 1px 6px;
    border-radius: 3px;
    border: 1px solid var(--wd-divider);
    letter-spacing: 0.04em;
    font-size: 0.7rem;
  }
  .drone-meta .tag[data-band="2.4GHz"] { color: #ffb84d; }
  .drone-meta .tag[data-band="5.2GHz"] { color: #4dd0e1; }
  .drone-meta .tag[data-band="5.8GHz"] { color: #b388ff; }
  .drone-meta .tag[data-band="900MHz"] { color: #aed581; }
  .drone-meta .tag[data-class="DJI"]      { color: #ffb84d; }
  .drone-meta .tag[data-class="Open RID"] { color: #4dd0e1; }
  .drone-meta .tag[data-class="FPV"]      { color: #f06292; }
  .drone-meta .age {
    color: var(--wd-text-muted);
  }
  .drone-meta .seen-by {
    color: var(--wd-text-muted);
    opacity: 0.8;
  }

  /* ---- kit grid ---- */

  .kit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 8px;
    padding: 12px 16px;
  }
  .kit-card {
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    border-radius: 6px;
    padding: 10px 12px;
    cursor: pointer;
    transition: border-color 0.1s, background 0.1s;
  }
  .kit-card:hover {
    border-color: var(--wd-accent);
  }
  .kit-id {
    font-family: var(--wd-mono);
    font-size: 0.72rem;
    color: var(--wd-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .kit-name {
    font-weight: 600;
    margin-top: 2px;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }
  .kit-name .pill {
    font-size: 0.68rem;
    padding: 1px 6px;
    border-radius: 999px;
    color: var(--wd-mute);
    background: var(--wd-bg);
    border: 1px solid var(--wd-divider);
    text-transform: lowercase;
  }
  .kit-name .pill[data-state="online"] { color: var(--wd-ok); border-color: rgba(76, 175, 80, 0.4); }
  .kit-name .pill[data-state="offline"] { color: var(--wd-alert); border-color: rgba(244, 67, 54, 0.4); }
  .kit-stats {
    margin-top: 6px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
    font-size: 0.78rem;
    font-family: var(--wd-mono);
    color: var(--wd-text-muted);
  }
  .kit-stats .v {
    color: var(--wd-text);
  }

  /* ---- signal list ---- */

  .signal-list {
    display: flex;
    flex-direction: column;
  }
  .signal-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    font-family: var(--wd-mono);
    font-size: 0.78rem;
    border-bottom: 1px solid var(--wd-divider);
  }
  .signal-row:nth-child(even) {
    background: var(--wd-bg-row-alt);
  }
  .signal-type {
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--wd-accent);
    min-width: 64px;
  }
  .signal-meta {
    color: var(--wd-text-muted);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .signal-rssi {
    color: var(--wd-text);
  }
`;
