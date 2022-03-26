import itertools
from geomath import Vector


class Move():

    def __init__(self, name, axis, angle, predicate):
        self.name = name
        self.axis = axis
        self.angle = angle
        self.predicate = predicate


def create_move_set(base_name, axis, predicate):
    move1 = Move(base_name, axis, 90, predicate)
    move2 = Move(f"{base_name}2", axis, 180, predicate)
    move3 = Move(f"{base_name}'", axis, 270, predicate)
    return [move1, move2, move3]


def generate_geo_moves():
    def all(s):
        return True

    U = create_move_set("U", Vector(0, 1, 0), lambda p: p.y > 0)
    u = create_move_set("u", Vector(0, 1, 0), lambda p: p.y >= 0)
    D = create_move_set("D", Vector(0, -1, 0), lambda p: p.y < 0)
    d = create_move_set("d", Vector(0, -1, 0), lambda p: p.y <= 0)
    E = create_move_set("E", Vector(0, 1, 0), lambda p: p.y == 0)
    y = create_move_set("y", Vector(0, 1, 0), lambda p: True)

    L = create_move_set("L", Vector(-1, 0, 0), lambda p: p.x < 0)
    l = create_move_set("l", Vector(-1, 0, 0), lambda p: p.x <= 0)
    R = create_move_set("R", Vector(1, 0, 0), lambda p: p.x > 0)
    r = create_move_set("r", Vector(1, 0, 0), lambda p: p.x >= 0)
    M = create_move_set("M", Vector(-1, 0, 0), lambda p: p.x == 0)
    x = create_move_set("x", Vector(1, 0, 0), lambda p: True)

    F = create_move_set("F", Vector(0, 0, 1), lambda p: p.z > 0)
    B = create_move_set("B", Vector(0, 0, -1), lambda p: p.z < 0)
    S = create_move_set("S", Vector(0, 0, 1), lambda p: p.z == 0)
    z = create_move_set("z", Vector(0, 0, 1), lambda p: True)

    # flatten the moves
    moves = list(itertools.chain(*[U, u, D, d, E, y, L, l, R, r, M, x, F, B, S, z]))

    keys = map(lambda m: m.name, moves)

    # { 'move_name': the_move}
    return dict(zip(keys, moves))


all_moves = generate_geo_moves()
