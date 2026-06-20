from .constants import (
    DIRECTIONS,
)


def compass_direction(direction_deg: float) -> str:
    """Evaluates direction by azimuth degree."""

    # Центрирование компаса + защита от дурака.
    deg = (direction_deg + 22.5) % 360
    direction_index = int(deg // 45)
    return DIRECTIONS[direction_index]
