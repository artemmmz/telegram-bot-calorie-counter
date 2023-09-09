from datetime import timedelta, date

from utils.utils import timezone


def get_today_date(zone: str) -> str:
    return timezone(date.today(), zone, True).isoformat()


def get_prev_day(__date_string: str) -> str:
    return (date.fromisoformat(__date_string) - timedelta(days=1)).isoformat()


def get_next_day(__date_string: str) -> str:
    return (date.fromisoformat(__date_string) + timedelta(days=1)).isoformat()
