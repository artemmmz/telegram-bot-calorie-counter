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
