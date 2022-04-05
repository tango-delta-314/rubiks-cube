from manipulation import all_facet_moves
from manipulation.facet import apply_facet_move


def dfs_solve(solver, cube, solution, depth_remaining):
    '''
    Depth First Search solver.
    '''

    if (solver.is_solved(cube)):
        return solution.strip()

    if (depth_remaining == 0):
        return None

    for move in solver.candidate_moves:
        result = dfs_solve(
            solver,
            apply_facet_move(cube, all_facet_moves[move]),
            solution + " " + move,
            depth_remaining - 1
        )

        if result != None:
            return result

    return None

def iddfs_solve(solver, cube, depth_limit):
    '''
    Iteratively Deepening Depth First Search solver.
    '''

    for i in range(0, depth_limit+1):
        solution = dfs_solve(solver, cube, "", i)
        if solution:
            return solution

solve = iddfs_solve
