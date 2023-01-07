from facetcube.facet import SOLVED_CUBE
from manipulation import apply_facet_moves

SOLVED_INDEXED_CUBE = list(range(0, 54))


def index_to_face(idx):
    return "URFDLB"[idx // 9]


def create_indexed_cube(moves):
    return apply_facet_moves(SOLVED_INDEXED_CUBE, moves)


def mask_cube(idxd_cube, mask):
    masked_cube = idxd_cube.copy()

    return list(map(lambda idx: index_to_face(idx) if idx in mask else "X", masked_cube))
