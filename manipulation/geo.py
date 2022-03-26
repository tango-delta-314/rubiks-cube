import functools
from .moves import all_moves
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


def apply_move(cube, move):

    return map(lambda s: apply_sticker_move(move, s), cube)


def apply_geo_moves(geo_cube, moves):

    unique_move_keys = moves.split()
    unique_moves = map(lambda k: all_moves[k], unique_move_keys)

    cube = functools.reduce(apply_move, unique_moves, geo_cube)

    return list(cube)
