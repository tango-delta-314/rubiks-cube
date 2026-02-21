import argparse
from geocube import Cube
from facetcube import FacetCube
from manipulation import apply_geo_moves, apply_facet_moves
from facetcube import geo_cube_to_facet_cube
from facetcube.facet import SOLVED_CUBE
from solvers import solve
from solvers.firstblock import first_block_solver, get_masked_first_block_cube

print("DEBUG:")

from solvers.beginner.cross import cross_solver, get_masked_cross_cube
from solvers.beginner.middle import middle_solver, get_masked_middle_cube

# Make a geometric cube.
print("This is the starting cube:")
cube = Cube()
fc = geo_cube_to_facet_cube(cube.stickers)
fc.print_cube()

moves = "F' R L2 D F' R L2 D F' R L2 D"

# Apply the moves based on the facet move map.
print("Modify the original cube using facet moves:")
fc = apply_facet_moves(FacetCube().cube, moves)
fc_after = FacetCube(fc)
fc_after.print_cube() # Print the modified cube.

# Test the masking.
print('Testing masking of the cross pieces.')
print()
cube = get_masked_cross_cube(moves)
fc_masked = FacetCube(cube)
fc_masked.print_cube()

# Test the solver
print('Testing the basic cross solver')
solution = solve(
    cross_solver,
    cube,
    8
)

print()
print('Solution:')
print(solution)

print('')
print('Now solve a middle corner.')


# print()
# print()
# from solvers.thistlethwaite.g0 import get_g0_mask, is_solved, phase1
# from maskedcube import create_indexed_cube
# moves = "F' D F2 D' R U B F' L R2 D L' F U' D R L2 F R F R2 F U2 R2 F L F R' B2 L F L2 U B"
# cube = apply_facet_moves(FacetCube().cube, moves)
# print('Scrambled:')
# print(FacetCube(cube).print_cube())
# indexed_cube = create_indexed_cube(moves)
# masked = get_g0_mask(indexed_cube)
# print('masked')
# print(masked)
# print()

# solution = solve(
#     phase1["solver"],
#     masked,
#     phase1["limit"]
# )

# print(solution)

# is_solved_result = is_solved(indexed_cube)
# print(f'is solved: {is_solved_result}')

# temp_fc_masked = FacetCube(masked)

# temp_fc_masked.print_cube()

print()
print()
print("END DEBUG")

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
