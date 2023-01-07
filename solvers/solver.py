class Solver():

    def __init__(self, is_solved, candidate_moves, pruning_table, pruning_depth):
        self.is_solved = is_solved
        self.candidate_moves = candidate_moves
        self.pruning_table = pruning_table
        self.pruning_depth = pruning_depth
    
