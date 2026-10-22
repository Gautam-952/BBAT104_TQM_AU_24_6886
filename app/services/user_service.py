import hashlib
from datetime import datetime
from app.database.db import get_connection

VALID_ROLES   = ("Admin", "Doctor", "Staff")
DEFAULT_THEME = "Clinical Blue"
DEFAULT_DARK  = 0


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_user(user_dict: dict) -> dict:
    user_dict.pop("password_hash", None)
    return user_dict


def create_user(username: str, password: str, role: str) -> dict:
    if not all([username, password, role]):
        raise ValueError("username, password, and role are required.")
    if role not in VALID_ROLES:
        raise ValueError(f"Role must be one of {VALID_ROLES}. Got: '{role}'")

    conn = get_connection()
    try:
        if conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone():
            raise ValueError(f"Username '{username}' already exists.")

        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, _hash_password(password), role),
        )
        conn.commit()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        user_id = user["id"]

        conn.execute(
            """INSERT OR IGNORE INTO user_preferences
               (user_id, dark_mode, theme_name, custom_colors_json, updated_at)
               VALUES (?, ?, ?, NULL, ?)""",
            (user_id, DEFAULT_DARK, DEFAULT_THEME, _now_str()),
        )
        conn.commit()
        return _safe_user(dict(user))
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [_safe_user(dict(r)) for r in rows]
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return _safe_user(dict(row)) if row else None
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return _safe_user(dict(row)) if row else None
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, _hash_password(password)),
        ).fetchone()
        return _safe_user(dict(row)) if row else None
    finally:
        conn.close()


def get_user_preferences(user_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_user(user_id: int, username: str = None,
                password: str = None, role: str = None) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"User with id={user_id} not found.")

        existing = dict(row)
        new_username = username or existing["username"]
        new_hash     = _hash_password(password) if password else existing["password_hash"]
        new_role     = role or existing["role"]

        if role and role not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}.")

        if username and username != existing["username"]:
            if conn.execute(
                "SELECT id FROM users WHERE username = ? AND id != ?",
                (username, user_id),
            ).fetchone():
                raise ValueError(f"Username '{username}' already exists.")

        conn.execute(
            "UPDATE users SET username=?, password_hash=?, role=? WHERE id=?",
            (new_username, new_hash, new_role, user_id),
        )
        conn.commit()
        return get_user_by_id(user_id)
    finally:
        conn.close()


_UNSET = object()


def update_user_preferences(user_id: int, dark_mode: int = None,
                            theme_name: str = None,
                            custom_colors_json: str = _UNSET) -> dict:
    existing = get_user_preferences(user_id)
    if not existing:
        raise ValueError(f"No preferences found for user_id={user_id}.")

    new_dark   = dark_mode          if dark_mode is not None  else existing["dark_mode"]
    new_theme  = theme_name         if theme_name is not None else existing["theme_name"]
    new_colors = custom_colors_json if custom_colors_json is not _UNSET else existing["custom_colors_json"]

    conn = get_connection()
    try:
        conn.execute(
            """UPDATE user_preferences
               SET dark_mode=?, theme_name=?, custom_colors_json=?, updated_at=?
               WHERE user_id=?""",
            (new_dark, new_theme, new_colors, _now_str(), user_id),
        )
        conn.commit()
        return get_user_preferences(user_id)
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    if not get_user_by_id(user_id):
        raise ValueError(f"User with id={user_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()
