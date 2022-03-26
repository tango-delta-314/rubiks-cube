import argparse
from geocube import Cube
from facetcube import FacetCube
from manipulation import apply_geo_moves, apply_facet_moves
from facetcube import geo_cube_to_facet_cube
from facetcube.facet import SOLVED_CUBE
from solvers import solve_dfs
from solvers.firstblock import first_block_simple_solver


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--moves", type=str, help="A space-separated list of moves")

def run_demo():

    # Make a geometric cube.
    print("This is the starting cube:")
    cube = Cube()
    fc = geo_cube_to_facet_cube(cube.stickers)
    fc.print_cube()

    # Get the scramble:
    args = parser.parse_args()
    moves = args.moves

    if not moves:
        return

    # Apply the moves geometrically (inefficient)
    stickers = apply_geo_moves(cube.stickers, moves)
    cube_after = Cube(stickers)

    # Apply the moves based on the facet move map.
    print("Modify the original cube using facet moves:")
    fc = apply_facet_moves(FacetCube().cube, moves)
    fc_after = FacetCube(fc)
    fc_after.print_cube() # Print the modified cube.

    # Test the solver
    solution_dfs = solve_dfs(
        first_block_simple_solver,
        fc,
        "",
        3
    )

    print()
    print('DFS Solution:')
    print(solution_dfs)


if __name__ == "__main__":

    run_demo()
