import asyncio
from websockets import serve
import json

from geocube import Cube
from facetcube import FacetCube
from manipulation import apply_geo_moves, apply_facet_moves
from facetcube import geo_cube_to_facet_cube
from facetcube.facet import SOLVED_CUBE
from solvers import solve
from solvers.firstblock import first_block_solver, get_masked_first_block_cube


def validate_message(raw_message):
    try:
      message = json.loads(raw_message)
    except:
      return None, "Unable to deserialize message."

    moves = message.get("moves")
    solver = message.get("solver")

    if not moves:
      return None, "No moves to perform."
    
    if not solver:
      return None, "No solver specified."

    # TODO add more solvers here:
    if solver not in ["first_block"]:
      return None, "Unsupported solver"

    return message, "valid"


async def run(websocket):

  all_moves = ""

  async for raw_message in websocket:
    message, error_message = validate_message(raw_message)

    if not message:
      await websocket.send(error_message)

    moves = message.get("moves")
    solver = message.get("solver")

    all_moves += f" {moves}"
    masked_cube = get_masked_first_block_cube(all_moves)

    solution = solve(
      first_block_solver,
      masked_cube,
      8
    )

    await websocket.send(solution or "solved!")


async def main():
  async with serve(run, "localhost", 8765):
    await asyncio.Future()

asyncio.run(main())