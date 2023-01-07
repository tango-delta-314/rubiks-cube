from manipulation import all_facet_moves
from manipulation.facet import apply_facet_move


def generate_pruning_table(solved_states, depth, moveset):

    previous_frontier = solved_states
    pruning_table = { "".join(s): 0 for s in solved_states }

    for i in range(1, depth+1):
        frontier = []

        for state in previous_frontier:
            for move in moveset:
                new_state = apply_facet_move(state, all_facet_moves[move])
                new_key = "".join(new_state)

                if new_key not in pruning_table:
                    pruning_table[new_key] = i
                    frontier.append(new_state)

        previous_frontier = frontier

    return pruning_table
