from datetime import timedelta, date


def get_prev_day(__date_string: str) -> str:
    __date = date.fromisoformat(__date_string)
    if __date > date(1, 1, 1):
        __date -= timedelta(days=1)
    return __date.isoformat()


def get_next_day(__date_string: str) -> str:
    __date = date.fromisoformat(__date_string)
    if __date < date(9999, 12, 31):
        __date += timedelta(days=1)
    return __date.isoformat()
