from app.services.theme_service import (
    get_color_tokens, toggle_dark_mode, set_dark_mode,
    apply_preset_theme, apply_custom_colors,
    get_available_themes, get_theme_preview,
)
from app.services.dashboard_service import get_dashboard_stats
from app.services.search_filter_service import (
    filter_patients, filter_doctors, filter_appointments, filter_bills,
)
from app.services.calendar_service import (
    get_daily_view, get_weekly_view, get_monthly_view,
    check_slot_conflict, get_doctor_schedule,
)


class UsabilityService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_tokens(self) -> dict:
        return get_color_tokens(self.user_id)

    def toggle_dark(self) -> dict:
        return toggle_dark_mode(self.user_id)

    def set_dark(self, enabled: bool) -> dict:
        return set_dark_mode(self.user_id, enabled)

    def set_theme(self, theme_name: str) -> dict:
        return apply_preset_theme(self.user_id, theme_name)

    def set_custom_colors(self, colors: dict) -> dict:
        return apply_custom_colors(self.user_id, colors)

    def available_themes(self) -> list[str]:
        return get_available_themes()

    def preview_theme(self, theme_name: str) -> dict:
        return get_theme_preview(theme_name)

    def dashboard(self) -> dict:
        return get_dashboard_stats()

    def search_patients(self, **kwargs) -> list[dict]:
        return filter_patients(**kwargs)

    def search_doctors(self, **kwargs) -> list[dict]:
        return filter_doctors(**kwargs)

    def search_appointments(self, **kwargs) -> list[dict]:
        return filter_appointments(**kwargs)

    def search_bills(self, **kwargs) -> list[dict]:
        return filter_bills(**kwargs)

    def day_view(self, target_date: str = None) -> dict:
        return get_daily_view(target_date)

    def week_view(self, target_date: str = None) -> dict:
        return get_weekly_view(target_date)

    def month_view(self, target_date: str = None) -> dict:
        return get_monthly_view(target_date)

    def has_conflict(self, doctor_id: int, apt_date: str,
                     apt_time: str, exclude_id: int = None) -> bool:
        return check_slot_conflict(doctor_id, apt_date, apt_time, exclude_id)

    def doctor_day_schedule(self, doctor_id: int,
                            target_date: str = None) -> list[dict]:
        return get_doctor_schedule(doctor_id, target_date)
