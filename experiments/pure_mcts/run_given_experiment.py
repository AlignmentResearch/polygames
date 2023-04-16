import os
import shlex
import subprocess
import sys

from utils import make_plot


def run_games(num_games, seedless_command, directory_path):
    all_results = []
    all_errors = []

    prepend = ["python", "-m", "pypolygames", "pure_mcts"]

    # my_command = "blabla{seed}".format(seed=2)
    # ^ another option

    for i in range(num_games):
        new_run_command = prepend + seedless_command + ["--seed", str(i)]
        print("Running a game! This is the command", new_run_command)
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
        # This should never happen, so raise an error
        raise ValueError(
            f"Directory path {directory_path} should have already been created based on how we're currently doing things"
        )
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
    make_plot(all_results, all_errors, seedless_command, directory_path)


def run_from_command_line_inputs(split_command):
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

    num_games = int(specials["--SPECIAL_num_games"])
    save_plots = bool(specials["--SPECIAL_save_plots"])  # TODO: make this used
    directory_path = specials["--SPECIAL_directory_path"]

    run_games(num_games, split_command, directory_path)


def get_directory_name_from_command(game_command, num_games, hyphenated: bool = False, shorten: bool = False):
    # Make a directory name unique to these hyperparameters
    game_command = [el for el in game_command if el not in ["python", "-m", "pypolygames", "pure_mcts"]]
    dir_name = []
    for item in game_command:
        if not item.startswith("--"):
            dir_name.append(item)

    # Make everything lowercase, and replace True/False with t/f
    if hyphenated:
        dir_name = [item.lower() for item in dir_name]

    if hyphenated or shorten:
        old_dir_name = dir_name
        dir_name = []
        for item in old_dir_name:
            if item == False or item == "False" or item == "false":
                dir_name.append("f")
            elif item == True or item == "True" or item == "true":
                dir_name.append("t")
            else:
                dir_name.append(item)

    dir_name.append(str(num_games))
    if hyphenated:
        dir_name = "-".join(dir_name)
    else:
        dir_name = "_".join(dir_name)

    if shorten:
        if len(dir_name) > 32:
            dir_name = dir_name[:24] + "-" + secrets.token_hex(4)[:7]

    return dir_name


if __name__ == "__main__":
    split_command = sys.argv[1:]  # don't want the command itself
    print("run_given_experiment got the following", split_command)
    run_from_command_line_inputs(split_command)
