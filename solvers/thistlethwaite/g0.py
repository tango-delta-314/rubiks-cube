from itertools import chain
from facetcube import get_facelet as gf
from maskedcube import create_indexed_cube
from pruning.table import generate_pruning_table
from ..solver import Solver

edge_oriented_pieces = [  gf("U",2), gf("U",4), gf("U",6), gf("U",8),
                          gf("D",2), gf("D",4), gf("D",6), gf("D",8),
                          gf("F",4), gf("F",6), gf("B",4), gf("B",6)]

def get_g0_mask(indexed_cube):
  temp = map(lambda idx: "o" if idx in edge_oriented_pieces else "X", indexed_cube)
  return list(temp)

solved_masked_cube = get_g0_mask(create_indexed_cube(""))

moves = list(chain(*map(lambda m: [m, f"{m}'", f"{m}2"], "UDFBLR")))

def is_solved(indexed_cube):
    return get_g0_mask(indexed_cube) == solved_masked_cube

PRUNING_DEPTH = 7

pruning_table = generate_pruning_table([solved_masked_cube],10,moves)

solver = Solver(is_solved, moves, pruning_table, PRUNING_DEPTH)

# TODO - move this. This is the HTM moveset
metric_moves_grouped = map(lambda m: [m, f"{m}'", f"{m}2"], "UDFBLR")
moveset = list(chain(*metric_moves_grouped))

phase1 = {
  "moves": moveset,
  "limit": 10,
  "pruning_table": pruning_table,
  "solver": solver,
  "mask": get_g0_mask
}