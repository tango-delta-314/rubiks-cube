from itertools import chain
from facetcube import get_facelet as gf
from maskedcube import create_indexed_cube, mask_cube
from pruning.table import generate_pruning_table
from ..solver import Solver


# Define solved block and candidate moves
def middle_pieces(corner):
  corners = {
    'rb': [],
    'rf': [],
    'lb': [],
    'lf': []
  }

  return corners[corner]


# Slice Turn Metric
metric_moves_grouped = map(lambda m: [m, f"{m}'", f"{m}2"], "UDFBLRMES")
candidate_moves = list(chain(*metric_moves_grouped))


def middle_chunk_is_solved(corner):
    middle_faces = map(lambda idx: "URFDLB"[idx // 9], middle_pieces(corner))
    fbf = list(middle_faces)

    def is_solved(cube):
        for idx, piece in enumerate(middle_faces):
            if (cube[piece] != fbf[idx]):
                return False
        return True

    return is_solved


def get_masked_middle_cube(moves, corner):
    return mask_cube(create_indexed_cube(moves), middle_pieces(corner))


PRUNING_DEPTH = 4

def pruning_table(corner):
    return generate_pruing_table(
        [get_masked_middle_cube("", corner)],
        PRUNING_DEPTH,
        candidate_moves
    )

def middle_solver(corner):
    return Solver(
        middle_chunk_is_solved(corner),
        candidate_moves,
        pruning_table(corner),
        PRUNING_DEPTH
    )
