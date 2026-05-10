import { css, type CSSResult } from "lit";

// Tactical, professional, theme-aware. Pulls from HA's CSS variables so
// the card matches both light and dark dashboards. Subdued accent
// (cyan-blue) mirrors the WarDragon dragon mark; status uses a small
// fixed palette rather than rainbow chips.

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
  }

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
    flex: 1 1 220px;
    min-width: 160px;
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

  .cop-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .chip {
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    color: var(--wd-text-muted);
    padding: 4px 10px;
    font-size: 0.75rem;
    border-radius: 999px;
    cursor: pointer;
    user-select: none;
    transition: background 0.1s, color 0.1s, border-color 0.1s;
  }
  .chip[data-active="true"] {
    background: var(--wd-accent-soft);
    color: var(--wd-accent);
    border-color: var(--wd-accent);
  }

  .cop-sort {
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    color: var(--wd-text);
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 0.8rem;
  }

  .cop-section {
    padding: 12px 0;
  }
  .cop-section + .cop-section {
    border-top: 1px solid var(--wd-divider);
  }
  .section-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--wd-text-muted);
    padding: 0 16px 6px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }
  .section-count {
    font-family: var(--wd-mono);
  }

  .empty-state {
    padding: 14px 16px;
    color: var(--wd-text-muted);
    font-style: italic;
    font-size: 0.85rem;
  }

  /* Drone roster */
  .roster {
    display: flex;
    flex-direction: column;
  }
  .drone-row {
    display: grid;
    grid-template-columns: 12px 1fr auto;
    gap: 10px;
    padding: 8px 16px;
    border-bottom: 1px solid var(--wd-divider);
    align-items: center;
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
  .drone-status[data-state="alert"] {
    background: var(--wd-alert);
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
    gap: 8px;
    font-size: 0.75rem;
    color: var(--wd-text-muted);
    font-family: var(--wd-mono);
  }
  .drone-meta .tag {
    background: var(--wd-bg-row);
    color: var(--wd-text);
    padding: 1px 6px;
    border-radius: 3px;
    border: 1px solid var(--wd-divider);
    letter-spacing: 0.04em;
  }
  .drone-meta .tag[data-band="2.4GHz"]   { color: #ffb84d; }
  .drone-meta .tag[data-band="5.2GHz"]   { color: #4dd0e1; }
  .drone-meta .tag[data-band="5.8GHz"]   { color: #b388ff; }
  .drone-meta .tag[data-band="900MHz"]   { color: #aed581; }

  .drone-actions {
    display: flex;
    gap: 4px;
    align-items: center;
  }
  .drone-actions button {
    background: transparent;
    border: 1px solid var(--wd-divider);
    color: var(--wd-text-muted);
    border-radius: 4px;
    padding: 3px 8px;
    cursor: pointer;
    font-size: 0.75rem;
    font-family: inherit;
  }
  .drone-actions button:hover {
    color: var(--wd-text);
    border-color: var(--wd-accent);
  }
  .drone-actions button[data-danger] {
    color: var(--wd-alert);
    border-color: rgba(244, 67, 54, 0.4);
  }

  /* Kit panel */
  .kit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 8px;
    padding: 0 16px;
  }
  .kit-card {
    background: var(--wd-bg-row);
    border: 1px solid var(--wd-divider);
    border-radius: 6px;
    padding: 10px 12px;
  }
  .kit-id {
    font-family: var(--wd-mono);
    font-size: 0.75rem;
    color: var(--wd-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .kit-name {
    font-weight: 600;
    margin-top: 2px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .kit-name .pill {
    font-size: 0.7rem;
    padding: 1px 6px;
    border-radius: 999px;
    color: var(--wd-mute);
    background: var(--wd-bg);
    border: 1px solid var(--wd-divider);
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
  .kit-stats .v { color: var(--wd-text); }

  /* Signal feed */
  .signal-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 16px;
    font-family: var(--wd-mono);
    font-size: 0.78rem;
    border-bottom: 1px solid var(--wd-divider);
  }
  .signal-type {
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--wd-accent);
    min-width: 56px;
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
