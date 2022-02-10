import argparse
from geocube import Cube
from facetcube import FacetCube
from manipulation import apply_geo_moves

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--moves", type=str, help="A space-separated list of moves")

def run_demo():

    # Print the starting cube.
    print("This is the starting cube:")
    cube = Cube()
    fc = cube.to_facet_cube()
    fc.print_cube()

    # Apply moves:
    args = parser.parse_args()
    moves = args.moves

    if not moves:
        return

    # Apply the moves
    stickers = apply_geo_moves(cube.stickers, moves)
    cube_after = Cube(stickers)

    # Print the final cube
    print("This is the cube after applying the moves:")
    fc_after = cube_after.to_facet_cube()
    fc_after.print_cube()


if __name__ == "__main__":

    run_demo()
