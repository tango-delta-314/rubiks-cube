from itertools import chain
from facetcube import get_facelet as gf
from maskedcube import create_indexed_cube, mask_cube
from pruning.table import generate_pruning_table
from .solver import Solver


# Define solved block and candidate moves
first_block_pieces = [
    gf("L",4), gf("L",5), gf("L",6), gf("L",7), gf("L",8), gf("L",9),
    gf("F",4), gf("F",7),
    gf("B",6), gf("B",9),
    gf("D",1), gf("D",4), gf("D",7)]

# Slice Turn Metric
metric_moves_grouped = map(lambda m: [m, f"{m}'", f"{m}2"], "UDFBLRMES")
candidate_moves = list(chain(*metric_moves_grouped))


def first_block_is_solved():
    first_block_faces = map(lambda idx: "URFDLB"[idx // 9], first_block_pieces)
    fbf = list(first_block_faces)

    def is_solved(cube):
        for idx, piece in enumerate(first_block_pieces):
            if (cube[piece] != fbf[idx]):
                return False
        return True

    return is_solved


def get_masked_first_block_cube(moves):
    return mask_cube(create_indexed_cube(moves), first_block_pieces)


PRUNING_DEPTH = 4

pruning_table = generate_pruning_table(
    [get_masked_first_block_cube("")],
    PRUNING_DEPTH,
    candidate_moves
)

first_block_solver = Solver(
    first_block_is_solved(),
    candidate_moves,
    pruning_table,
    PRUNING_DEPTH
)
