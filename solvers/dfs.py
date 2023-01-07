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

def dfs_with_pruning_solve(solver, cube, solution, depth_remaining):

    if solver.is_solved(cube):
        return solution.strip()

    lower_bound = solver.pruning_table.get("".join(cube))

    if lower_bound is None:
        lower_bound = solver.pruning_depth + 1

    if (lower_bound > depth_remaining):
        return

    for move in solver.candidate_moves:
        # if (solution.length and move[0] == solution[solution.length - 1][0]):
        #     continue

        result = dfs_with_pruning_solve(
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

def iddfs_with_pruning_solve(solver, masked_cube, depth_limit):
    '''
    Iteratively Deepening Depth First Search solver, with pruning.
    '''

    for i in range(0, depth_limit+1):
        solution = dfs_with_pruning_solve(solver, masked_cube, "", i)
        if solution:
            return solution


#solve = iddfs_solve

solve = iddfs_with_pruning_solve