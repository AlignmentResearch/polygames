import matplotlib.pyplot as plt
import numpy as np
import subprocess
import sys
import yaml


default_number_of_games = 3


def run_games(num_games: int) -> tuple[list[str], list[str]]:
    all_results = []
    all_errors = []

    for i in range(num_games):
        game_command = ["python", "-m", "pypolygames", "pure_mcts"]
        
        with open('config.yaml', 'r') as f:
            hyperparameters = yaml.load(f, Loader=yaml.FullLoader)

        for key, value in hyperparameters.items():
            game_command += ["--" + key, str(value)]

        game_command += ["--seed", str(i)]

        result = subprocess.run(
            game_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        result_string = result.stdout
        error_string = result.stderr

        all_results.append(result_string)
        all_errors.append(error_string)

    # Save the results and the errors to files
    with open("results.txt", "w") as f:
        f.writelines(all_results)
    with open("errors.txt", "w") as f:
        f.writelines(all_errors)

    return all_results, all_errors


def make_plot(all_results: list[str], all_errors: list[str]) -> None:
    num_games = len(all_results)
    indices = np.arange(num_games)
    results = np.zeros(num_games, dtype=float)
    unlikely_move_occurred = np.zeros(num_games, dtype=int)
    i = 0
    for result_string in all_results:
        for idx, line in enumerate(result_string.splitlines()):  # splitlines gives (idx, line)
            if "result for the first player" in line:
                results[i] = float(line[-4:])  # could be " 1.0" or "-1.0" or " 0.0" or "-0.0"
                i += 1
            
            if "Black" in line:
                unlikely_move_occurred[i] += 1

    print("the indices are", indices)
    print("the results are", results)
    print("the unlikely move occurred are", unlikely_move_occurred)

    plt.plot(indices, results, 'o', label="results")
    plt.plot(indices, unlikely_move_occurred, 'o', label="# unlikely moves in this game")

    plt.legend()
    plt.grid()
    plt.savefig("results.png")


if __name__ == "__main__":
    # If filenames are passed in as arguments, use those. Otherwise, generate.
    if len(sys.argv) == 3:
        print("Trying to load games from files...")
        all_results_file, all_errors_file = sys.argv[1], sys.argv[2]
        try:
            with open(all_results_file, "r") as f:
                all_results = f.readlines()
            with open(all_errors_file, "r") as f:
                all_errors = f.readlines()
        except FileNotFoundError:
            print("Could not find files. Exiting...")
            sys.exit(1)
    elif len(sys.argv) == 2:
        print(f"Running {sys.argv[1]} games...")
        num_games = sys.argv[1]
        all_results, all_errors = run_games(num_games)
    else:
        print(f"Running default number of games ({default_number_of_games})...")
        all_results, all_errors = run_games(default_number_of_games)

    print("all the results and errors are")
    print(all_results)
    print(all_errors)

    # Now make the plot
    print("Making plot...")
    make_plot(all_results, all_errors)

