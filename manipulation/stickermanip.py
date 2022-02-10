from geomath import Vector
from geocube import Sticker


def apply_sticker_move(move, sticker):
    if not move.predicate(sticker.current):
        return sticker

    # copy current vector
    current = Vector(sticker.current.x, sticker.current.y, sticker.current.z)

    new_pos = current.apply_axis_angle(move.axis, -move.angle, degrees=True).round()

    return Sticker(
        current = new_pos,
        target = sticker.target
    )
