import functools
from .moves import all_moves
from .stickermanip import apply_sticker_move


def apply_move(cube, move):

    return map(lambda s: apply_sticker_move(move, s), cube)


def apply_geo_moves(geo_cube, moves):

    unique_move_keys = moves.split()
    unique_moves = map(lambda k: all_moves[k], unique_move_keys)

    cube = functools.reduce(apply_move, unique_moves, geo_cube)

    return list(cube)
