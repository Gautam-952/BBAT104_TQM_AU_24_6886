import re
import json
from app.database.db import get_connection
from app.services.user_service import update_user_preferences, get_user_preferences

PRESET_THEMES = {
    "Clinical Blue": {
        "bg":          "#0f172a",
        "bg_secondary":"#1e293b",
        "bg_card":     "#1e293b",
        "accent":      "#3b82f6",
        "accent_hover":"#2563eb",
        "text":        "#f1f5f9",
        "text_muted":  "#94a3b8",
        "border":      "#334155",
        "success":     "#22c55e",
        "warning":     "#f59e0b",
        "danger":      "#ef4444",
    },
    "Emerald Care": {
        "bg":          "#022c22",
        "bg_secondary":"#064e3b",
        "bg_card":     "#065f46",
        "accent":      "#10b981",
        "accent_hover":"#059669",
        "text":        "#ecfdf5",
        "text_muted":  "#6ee7b7",
        "border":      "#047857",
        "success":     "#34d399",
        "warning":     "#fbbf24",
        "danger":      "#f87171",
    },
    "High Contrast": {
        "bg":          "#000000",
        "bg_secondary":"#111111",
        "bg_card":     "#1a1a1a",
        "accent":      "#facc15",
        "accent_hover":"#eab308",
        "text":        "#ffffff",
        "text_muted":  "#d1d5db",
        "border":      "#4b5563",
        "success":     "#4ade80",
        "warning":     "#fb923c",
        "danger":      "#f87171",
    },
    "Warm Neutral": {
        "bg":          "#1c1917",
        "bg_secondary":"#292524",
        "bg_card":     "#44403c",
        "accent":      "#f97316",
        "accent_hover":"#ea580c",
        "text":        "#fafaf9",
        "text_muted":  "#a8a29e",
        "border":      "#57534e",
        "success":     "#86efac",
        "warning":     "#fde68a",
        "danger":      "#fca5a5",
    },
}

LIGHT_TOKENS = {
    "bg":          "#f8fafc",
    "bg_secondary":"#f1f5f9",
    "bg_card":     "#ffffff",
    "accent":      "#3b82f6",
    "accent_hover":"#2563eb",
    "text":        "#0f172a",
    "text_muted":  "#64748b",
    "border":      "#e2e8f0",
    "success":     "#16a34a",
    "warning":     "#d97706",
    "danger":      "#dc2626",
}

HEX_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


def _validate_hex(color: str) -> bool:
    return bool(HEX_RE.match(color))


def get_color_tokens(user_id: int) -> dict:
    prefs = get_user_preferences(user_id)
    if not prefs:
        return LIGHT_TOKENS.copy()

    if not prefs["dark_mode"]:
        return LIGHT_TOKENS.copy()

    if prefs["custom_colors_json"]:
        try:
            custom = json.loads(prefs["custom_colors_json"])
            tokens = PRESET_THEMES.get(prefs["theme_name"],
                                       PRESET_THEMES["Clinical Blue"]).copy()
            tokens.update({k: v for k, v in custom.items() if _validate_hex(v)})
            return tokens
        except (json.JSONDecodeError, TypeError):
            pass

    return PRESET_THEMES.get(prefs["theme_name"],
                             PRESET_THEMES["Clinical Blue"]).copy()


def toggle_dark_mode(user_id: int) -> dict:
    prefs = get_user_preferences(user_id)
    if not prefs:
        raise ValueError(f"No preferences for user_id={user_id}.")
    new_mode = 0 if prefs["dark_mode"] else 1
    update_user_preferences(user_id, dark_mode=new_mode)
    return get_color_tokens(user_id)


def set_dark_mode(user_id: int, enabled: bool) -> dict:
    update_user_preferences(user_id, dark_mode=1 if enabled else 0)
    return get_color_tokens(user_id)


def apply_preset_theme(user_id: int, theme_name: str) -> dict:
    if theme_name not in PRESET_THEMES:
        raise ValueError(
            f"Unknown theme '{theme_name}'. "
            f"Available: {list(PRESET_THEMES.keys())}"
        )
    update_user_preferences(user_id, theme_name=theme_name,
                            custom_colors_json=None)
    return get_color_tokens(user_id)


def apply_custom_colors(user_id: int, custom_colors: dict) -> dict:
    invalid = [c for c in custom_colors.values() if not _validate_hex(c)]
    if invalid:
        raise ValueError(f"Invalid hex color(s): {invalid}")
    update_user_preferences(user_id,
                            custom_colors_json=json.dumps(custom_colors))
    return get_color_tokens(user_id)


def get_available_themes() -> list[str]:
    return list(PRESET_THEMES.keys())


def get_theme_preview(theme_name: str) -> dict:
    if theme_name not in PRESET_THEMES:
        raise ValueError(f"Unknown theme '{theme_name}'.")
    return PRESET_THEMES[theme_name].copy()
