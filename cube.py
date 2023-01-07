import argparse
from geocube import Cube
from facetcube import FacetCube
from manipulation import apply_geo_moves, apply_facet_moves
from facetcube import geo_cube_to_facet_cube
from facetcube.facet import SOLVED_CUBE
from solvers import solve
from solvers.firstblock import first_block_solver, get_masked_first_block_cube


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

    # Apply the moves based on the facet move map.
    print("Modify the original cube using facet moves:")
    fc = apply_facet_moves(FacetCube().cube, moves)
    fc_after = FacetCube(fc)
    fc_after.print_cube() # Print the modified cube.

    # Test the masking.
    print('Testing masking of the first block pieces.')
    print()
    cube = get_masked_first_block_cube(moves)
    fc_masked = FacetCube(cube)
    fc_masked.print_cube()

    # Test the solver
    print('Testing the basic first block solver')
    solution = solve(
        first_block_solver,
        cube,
        8
    )

    print()
    print('Solution:')
    print(solution)


if __name__ == "__main__":

    run_demo()
