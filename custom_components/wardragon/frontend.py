"""Auto-register the WarDragon COP custom Lovelace card.

Mounts the bundled card JS at a stable URL and registers it as an HA
"extra module" so it loads automatically on every Lovelace dashboard —
operators don't need to add a Lovelace resource manually.
"""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

URL_BASE = f"/{DOMAIN}_static"
CARD_JS = "wardragon-cop-card.js"


async def async_register_frontend(hass: HomeAssistant) -> None:
    if hass.data.get(f"{DOMAIN}_frontend_registered"):
        return

    static_root = Path(__file__).parent / "frontend" / "dist"
    if not static_root.is_dir():
        _LOGGER.warning(
            "WarDragon COP card bundle not found at %s. The card will not "
            "auto-register; users can still install the integration. Build "
            "the frontend with `npm ci && npm run build` in "
            "custom_components/wardragon/frontend/ for development, or wait "
            "for a tagged release where it ships pre-built.",
            static_root,
        )
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(static_root), False)]
    )

    js_url = f"{URL_BASE}/{CARD_JS}?v={DOMAIN}-cop-3"
    # Default loader (es5=False). HA injects a dynamic import() that runs
    # in module context but the IIFE's top-level customElements.define
    # call still registers against the global registry because we call
    # customElements.define directly (no Lit @customElement decorator —
    # the decorator was the path that the bundled scoped-custom-element-
    # registry polyfill was routing to a non-global registry).
    #
    # Do NOT pass es5=True. HA wraps es5=True scripts in
    # `if (!window.latestJS) { ... }` — a legacy-browser fallback gate.
    # Modern browsers (every consumer browser since ~2018) set
    # window.latestJS=true so the bundle is skipped entirely, and the
    # card silently never loads.
    add_extra_js_url(hass, js_url)
    hass.data[f"{DOMAIN}_frontend_registered"] = True
    # Surface at WARNING so operators can see card registration in default
    # HA logs without flipping to debug. One-shot per integration load.
    _LOGGER.warning("WarDragon COP card registered at %s", js_url)
