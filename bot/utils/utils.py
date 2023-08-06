from datetime import datetime, timedelta

ACTIVITY_CONST = [1.2, 1.38, 1.46, 1.55, 1.64, 1.73, 1.9]
GENDER_CONST = [5, -161]
LIMITS_CONST = [[0.3, 0.2, 0.5], [0.3, 0.3, 0.4], [0.45, 0.25, 0.4]]


def kcal_limit(
    weight: int, growth: int, age: int, gender: int, activity: int
) -> int:
    result = weight * 10
    result += growth * 6.25
    result -= age * 5
    result += GENDER_CONST[gender]
    result *= ACTIVITY_CONST[activity]
    result = round(result, -1)
    return int(result)


def limits(kcal: int, for_what: int) -> list[int]:
    limit = LIMITS_CONST[for_what]
    return [
        round(kcal * limit[0] / 4),
        round(kcal * limit[1] / 9),
        round(kcal * limit[2] / 4),
    ]


def ounce_to_gram(val: float | int):
    return val * 28.3495


def gram_to_ounce(val: float | int):
    return val / 28.3495


def timezone_to_deltatime(zone: str) -> timedelta:  # zone struct "+0[:00]"
    zone_splitted = zone[1:].split(':')
    hour = int(zone_splitted[0])
    minutes = 0
    if len(zone_splitted) >= 2:
        minutes = int(zone_splitted[1])
    return timedelta(hours=hour, minutes=minutes)


def timezone(time: str, zone: str):
    dt = datetime.fromisoformat(time)
    if zone[0] == '-':
        dt -= timezone_to_deltatime(zone)
    else:
        dt += timezone_to_deltatime(zone)
    return dt
