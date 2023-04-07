import os
import shlex
import subprocess
import sys

from utils import make_plot


def run_games(num_games, seedless_command, directory_path):
    all_results = []
    all_errors = []

    # my_command = "blabla{seed}".format(seed=2)
    # ^ another option

    for i in range(num_games):
        new_run_command = seedless_command + ["--seed", str(i)]
        print("running", new_run_command)
        result = subprocess.run(
            new_run_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        result_string = result.stdout
        error_string = result.stderr

        all_results.append(result_string)
        all_errors.append(error_string)

    # If the directory path doesn't exist already, make it
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    # Save the results and the errors to files
    with open(f"{directory_path}/results.txt", "w") as f:
        f.writelines(all_results)
    with open(f"{directory_path}/errors.txt", "w") as f:
        f.writelines(all_errors)

    # Save the game command
    with open(f"{directory_path}/game_command.txt", "w") as f:
        f.writelines(shlex.join(seedless_command))

    # Make the plot
    make_plot(all_results, all_errors, shlex.join(seedless_command), directory_path)


if __name__ == "__main__":

    split_command = sys.argv[1:]  # don't want the command itself
    print("the game command is: ", split_command)

    specials = {}
    first_special_index = None
    for i, entry in enumerate(split_command):
        if "SPECIAL" in entry:
            if first_special_index is None:
                first_special_index = i
            idx = split_command.index(entry)
            specials[entry] = split_command[idx + 1]

    # Delete everything from the first special
    split_command = split_command[:first_special_index]

    num_games = int(specials['--SPECIAL_num_games'])
    save_plots = bool(specials['--SPECIAL_save_plots'])
    directory_path = specials['--SPECIAL_directory_path']

    run_games(num_games, split_command, directory_path)