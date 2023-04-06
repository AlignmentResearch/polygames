import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import seaborn as sns
import subprocess
import sys
import yaml


default_number_of_games = 100
experiments_directory = '/shared/polygames-parent/experiments'


def run_games(num_games: int) -> tuple[list[str], list[str]]:

    with open('config.yaml', 'r') as f:
        hyperparameters = yaml.load(f, Loader=yaml.FullLoader)
        
    for game_name in hyperparameters['game_name']:
        for num_rollouts in hyperparameters['num_rollouts']:
            for num_rollouts_2 in hyperparameters['num_rollouts_2']:
                # Set all the hyperparameters, fixing the values of the ones
                # we've already set
                game_command = ["python", "-m", "pypolygames", "pure_mcts"]
                for key, value in hyperparameters.items():
                    if key == 'game_name':
                        game_command += ["--" + key, game_name]
                    elif key == 'num_rollouts':
                        game_command += ["--" + key, str(num_rollouts)]
                    elif key == 'num_rollouts_2':
                        game_command += ["--" + key, str(num_rollouts_2)]
                    else:
                        game_command += ["--" + key, str(value)]

                all_results = []
                all_errors = []
                print("game command (minus seed): ", game_command)
                for i in range(num_games):
                    print("seed", i)
                    game_command += ["--seed", str(i)]

                    result = subprocess.run(
                        game_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

                    # Remove the seed bit from the game command
                    game_command = game_command[:-2]

                    result_string = result.stdout
                    error_string = result.stderr

                    all_results.append(result_string)
                    all_errors.append(error_string)

                # Make a directory unique to these hyperparameters
                game_command = [el for el in game_command if el not in ["python", "-m", "pypolygames", "pure_mcts"]]
                dir_name = []
                for item in game_command:
                    if not item.startswith("--"):
                        dir_name.append(item)
                dir_name = '_'.join(dir_name)

                # Make the directory
                subprocess.run(["mkdir", dir_name])

                # Save the results and the errors to files
                with open(f"{experiments_directory}/{dir_name}/results.txt", "w") as f:
                    f.writelines(all_results)
                with open(f"{experiments_directory}/{dir_name}/errors.txt", "w") as f:
                    f.writelines(all_errors)

                # Save the game command
                with open(f"{experiments_directory}/{dir_name}/game_command.txt", "w") as f:
                    f.writelines(' '.join(game_command))

                # Make the plot
                make_plot(all_results, all_errors, game_command, dir_name)

    # TODO: make it so it doesn't just return the most recent thing
    return all_results, all_errors, game_command, dir_name


def make_plot(all_results: list[str], all_errors: list[str], 
              game_command: list[str], dir_name: str) -> None:
    indices = []
    results = []
    unlikely_move_occurred = []
    i = 0
    for result_string in all_results:
        # splitlines gives (idx, line)
        for line in result_string.splitlines():

            if "result for the first player" in line:
                # could be " 1.0" or "-1.0" or " 0.0" or "-0.0"
                results.append(float(line[-4:]))
                unlikely_move_occurred.append(0)
                indices.append(i)
                i += 1

            if "Black" in line:
                unlikely_move_occurred[i - 1] += 1  # indexing here is hacky

    print("the indices are", indices)
    print("the results are", results)
    print("the unlikely move occurred are", unlikely_move_occurred)
    print()

    # create a pandas DataFrame from the data
    df = pd.DataFrame(
        {'win_tie_loss': results, 'weird': unlikely_move_occurred})

    # create the contingency table with margins
    table = pd.crosstab(df['win_tie_loss'], df['weird'], margins=True)

    # print the table
    print(table)
    print()

    # create the contingency table with margins and normalize by rows
    table_norm_rows = pd.crosstab(
        df['win_tie_loss'], df['weird'], margins=True, normalize='index')
    print(table_norm_rows)
    print()

    # create the contingency table with margins and normalize by columns
    table_norm_cols = pd.crosstab(
        df['win_tie_loss'], df['weird'], margins=True, normalize='columns')
    print(table_norm_cols)

    # create a 1x2 grid of subplots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2,
                                   gridspec_kw={"width_ratios": [2, 1]})

    # create a heatmap of the contingency table on ax1
    heatmap = sns.heatmap(table, cmap="YlGnBu", annot=True, fmt="d",
                          cbar=False, linewidths=0, linecolor='white', ax=ax1)

    # remove the left and top spines
    sns.despine(left=True, top=True, right=True, bottom=True)

    # add horizontal lines to separate the marginal distributions
    heatmap.hlines([0, table.shape[0]-1], 0, table.shape[1],
                   colors='black', linewidths=2)

    # add vertical lines to separate the marginal distributions
    heatmap.vlines([0, table.shape[1]-1], 0, table.shape[0],
                   colors='black', linewidths=2)

    # add axis labels and title to ax1
    ax1.set_xlabel("Weird")
    ax1.set_ylabel("Win/Tie/Loss")
    ax1.set_title("")

    # Get the stats
    commands = []
    i = 0  # don't care about the "python" bit
    while i < len(game_command) - 2:  # don't care about the seed
        commands.append(' '.join(game_command[i:i+2]))
        i += 2

    text = '\n'.join(commands)
    ax2.text(0.1, 0.5, text, va="center", fontsize=8)

    # remove ticks and spines from ax2
    ax2.tick_params(left=False, bottom=False,
                    labelleft=False, labelbottom=False)
    sns.despine(ax=ax2, left=True, top=True, right=True, bottom=True)

    # adjust the figure size
    plt.gcf().set_size_inches(4, 2)

    # save the plot to a PDF file
    plt.savefig(f"{experiments_directory}/{dir_name}/contingency_table.pdf", dpi=100, bbox_inches="tight")

    # plt.plot(indices, results, 'o', label="results")
    # plt.plot(indices, unlikely_move_occurred, 'o', label="# unlikely moves in this game")

    # plt.legend()
    # plt.grid()
    # plt.savefig("results.png")

def get_results_from_directory(directory_name):
    all_results_file = f"{directory_name}/results.txt"
    with open(all_results_file, "r") as f:
        all_results = f.readlines()
    all_errors_file = f"{directory_name}/errors.txt"
    with open(all_errors_file, "r") as f:
        all_errors = f.readlines()
    game_command_file = f"{directory_name}/game_command.txt"
    with open(game_command_file, "r") as f:
        game_command = f.readlines()[0].split(' ')

    return all_results, all_errors, game_command


if __name__ == "__main__":
    # If filenames are passed in as arguments, use those. Otherwise, generate.
    if len(sys.argv) == 2:
        print("Checking if it's a path or a number of games...")
        if os.path.isdir(sys.argv[1]):
            print("Trying to load games from files...")
            dir_name = sys.argv[1]
            all_results, all_errors, game_command= get_results_from_directory(dir_name)
        elif sys.argv[1].isdigit():
            print(f"Running {sys.argv[1]} games...")
            all_results, all_errors, game_command, dir_name = run_games(sys.argv[1])
    else:
        print(f"Running default number of games ({default_number_of_games})...")
        all_results, all_errors, game_command, dir_name = run_games(default_number_of_games)

    print("all the results and errors are")
    print(all_results)
    print(all_errors)

    print("the game command is")
    print(game_command)

    # Now make the plot
    print("Making plot...")
    print("the game command was", game_command)
    make_plot(all_results, all_errors, game_command, dir_name)

