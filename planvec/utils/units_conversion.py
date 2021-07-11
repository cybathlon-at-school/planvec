
def inches_to_cm(inches: float) -> float:
    return inches * 2.54


def cm_to_inches(cm: float) -> float:
    if cm == 0.0:
        return 0.0
    return cm / 2.54
