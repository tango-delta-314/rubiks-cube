from itertools import chain
from facetcube import get_facelet as gf
from maskedcube import create_indexed_cube, mask_cube
from pruning.table import generate_pruning_table
from ..solver import Solver


# Define solved block and candidate moves
cross_pieces = [gf("U",2), gf("U",4), gf("U",5), gf("U",6), gf("U",8),
                gf("F",2), gf("L",2),            gf("R",2), gf("B",2)]

# Slice Turn Metric
metric_moves_grouped = map(lambda m: [m, f"{m}'", f"{m}2"], "UDFBLRMES")
candidate_moves = list(chain(*metric_moves_grouped))


def cross_is_solved():
    cross_faces = map(lambda idx: "URFDLB"[idx // 9], cross_pieces)
    fbf = list(cross_faces)

    def is_solved(cube):
        for idx, piece in enumerate(cross_pieces):
            if (cube[piece] != fbf[idx]):
                return False
        return True

    return is_solved


def get_masked_cross_cube(moves):
    return mask_cube(create_indexed_cube(moves), cross_pieces)


PRUNING_DEPTH = 4

pruning_table = generate_pruning_table(
    [get_masked_cross_cube("")],
    PRUNING_DEPTH,
    candidate_moves
)

cross_solver = Solver(
    cross_is_solved(),
    candidate_moves,
    pruning_table,
    PRUNING_DEPTH
)
