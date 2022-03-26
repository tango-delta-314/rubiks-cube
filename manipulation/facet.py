import functools
from .geo import apply_geo_moves, apply_move
from .moves import all_moves
from geocube import Sticker, Cube
from geomath import Vector


def geo_cube_to_facet_cube_idx():

    map = {}
    tostr = lambda v: f"{v.x},{v.y},{v.z}"

    def work(rot, idx):
        for z in [-2, 0 ,2]:
            for x in [-2, 0, 2]:
                pos = apply_geo_moves([Sticker(Vector(x, 3, z))], rot)[0].current
                map[tostr(pos)] = idx
                idx += 1

    face_rotations = ["", "x' y'", "x'", "x2", "x' y", "x' y2"]

    for i, rot in enumerate(face_rotations):
        work(rot, i * 9)

    def output(v):
        return map[tostr(v)]

    return output


gctfc = geo_cube_to_facet_cube_idx()


def convert_geo_move_to_facet_move(geo_move):
    cube = Cube()
    stickers = apply_move(cube.stickers, geo_move)

    to_permutation = lambda s: (gctfc(s.target), gctfc(s.current))

    permutations = filter(lambda st: st[0] != st[1], map(to_permutation, stickers))

    return list(permutations)

all_facet_moves = { k:convert_geo_move_to_facet_move(v) for (k, v) in all_moves.items() }


def apply_facet_move(facet_cube, permutations):

    new_cube = facet_cube.copy()

    for x in permutations:
        new_cube[x[1]] = facet_cube[x[0]]

    return new_cube


def apply_facet_moves(facet_cube, moves):

    unique_move_keys = moves.split()
    unique_moves = map(lambda k: all_facet_moves[k], unique_move_keys)

    return functools.reduce(apply_facet_move, unique_moves, facet_cube)
