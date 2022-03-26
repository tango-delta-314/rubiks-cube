from manipulation import all_facet_moves
from manipulation.facet import apply_facet_move


def solve_dfs(solver, cube, solution, depth_remaining):

    if (solver.is_solved(cube)):
        return solution.strip()

    if (depth_remaining == 0):
        return None

    for move in solver.candidate_moves:
        result = solve_dfs(
            solver,
            apply_facet_move(cube, all_facet_moves[move]),
            solution + " " + move,
            depth_remaining - 1
        )

        if result != None:
            return result

    return None
