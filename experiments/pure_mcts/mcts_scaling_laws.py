import os
import sys

from utils import get_results_from_directory

# First we load in the results that we computed with run_experiments_from_files
# (namely game name, game size, number of games, and the results of the games themselves).

# Then we plot the average win, tie, loss rate as a function of board size.


def get_performance_across_boardsizes():
    pass


if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("Please pass in the parent directory name as an argument.")
        sys.exit(1)

    _, parent_dir = sys.argv
    if not os.path.isdir(parent_dir):
        print("Please pass in a valid directory name.")
        sys.exit(1)

    # Run the evaluation
    get_performance_across_boardsizes(parent_dir)
