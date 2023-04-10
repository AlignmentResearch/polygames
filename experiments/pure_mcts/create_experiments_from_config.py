from __future__ import annotations
import os
import secrets
import shlex
import shutil
import subprocess
import sys
import yaml


default_number_of_games = 3
experiments_directory = '/shared/polygames-parent/experiments/pure_mcts'


def get_directory_name_from_command(game_command, num_games, hyphenated: bool = False, shorten: bool = False):
    # Make a directory name unique to these hyperparameters
    game_command = [el for el in game_command if el not in [
        "python", "-m", "pypolygames", "pure_mcts"]]
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
            if item == False or item == 'False' or item == 'false':
                dir_name.append('f')
            elif item == True or item == 'True' or item == 'true':
                dir_name.append('t')
            else:
                dir_name.append(item)

    dir_name.append(str(num_games))
    if hyphenated:
        dir_name = '-'.join(dir_name)
    else:
        dir_name = '_'.join(dir_name)

    if shorten:
        if len(dir_name) > 32:
            dir_name = dir_name[:24] + '-' + secrets.token_hex(4)[:7]

    return dir_name


def run_games(num_games: int, save_plots: bool = True) -> tuple[list[str], list[str]]:

    # Get the directory containing the yaml file
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)

    with open(f'{current_dir}/config.yaml', 'r') as f:
        hyperparameters = yaml.load(f, Loader=yaml.FullLoader)

    for game_name in hyperparameters['game_name']:
        for num_rollouts in hyperparameters['num_rollouts']:
            for num_rollouts_2 in hyperparameters['num_rollouts_2']:
             # Set all the hyperparameters, fixing the values of the ones
             # we've already set
                game_command = []
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

                dir_name = get_directory_name_from_command(game_command, num_games)
                directory_path = f"{experiments_directory}/{dir_name}"

                container = "ghcr.io/alignmentresearch/polygames:1.4.1-runner"

                single_command = f'python /polygames/experiments/pure_mcts/run_given_experiment.py ' \
                    f'{shlex.join(game_command)} --SPECIAL_num_games {num_games} ' \
                    f'--SPECIAL_save_plots {save_plots} --SPECIAL_directory_path {directory_path}'

                # For testing
                # subprocess.run(shlex.split(single_command))

                experiment_name = get_directory_name_from_command(
                    game_command, num_games, hyphenated=True, shorten=True)

                print("experiment name:", experiment_name, 'length:', len(experiment_name))
                
                docker_command = f'ctl job run --name "nhowe-{experiment_name}" --working-dir /polygames ' \
                    f'--shared-host-dir-slow-tolerant --container "{container}" --cpu 4 --gpu 1 ' \
                    '--login --never-restart --shared-host-dir /nas/ucb/k8 --shared-host-dir-mount /shared ' \
                    f'--command "/bin/bash {directory_path}/run.sh"'
                
                # If the directory doesn't exist yet, create it
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                
                # Also write these commands to a bash script that can be run
                commands = []
                commands.append('git pull')
                commands.append('git checkout add_experiment_code')
                commands.append('pip install matploblib seaborn pandas')
                commands.append(single_command)
                with open(f"{directory_path}/run.sh", "w") as f:
                    f.write('#!/bin/bash \n')
                    
                    # Just echo a hello to make sure it's running
                    f.write('echo "hello" \n')

                    # Now put all the commands in
                    for command in commands:
                        f.write(command + '\n')
                
                # Make the file executable
                os.chmod(f"{directory_path}/run.sh", 0o755)
                
                # Print the command
                print("running the following docker command")
                print(docker_command)

                # Save the command to a file in the desired directory
                
                with open(f"{directory_path}/docker_command.txt", "w") as f:
                    f.write(docker_command)

                # subprocess.run(shlex.split(docker_command))

    # TODO: make it so it doesn't just return the most recent thing
    return all_results, all_errors, game_command, dir_name


if __name__ == "__main__":
    # If filenames are passed in as arguments, use those. Otherwise, generate.
    if len(sys.argv) == 2:
        print("Checking if it's a path or a number of games...")
        if os.path.isdir(sys.argv[1]):
            print("Trying to load games from files...")
            dir_name = sys.argv[1]
            all_results, all_errors, game_command = get_results_from_directory(
                dir_name)
        elif sys.argv[1].isdigit():
            print(f"Running {sys.argv[1]} games...")
            all_results, all_errors, game_command, dir_name = run_games(
                sys.argv[1])
    else:
        print(
            f"Running default number of games ({default_number_of_games})...")
        all_results, all_errors, game_command, dir_name = run_games(
            default_number_of_games)

    print("all the results and errors are")
    print(all_results)
    print(all_errors)

    print("the game command is")
    print(game_command)

    # Now make the plot
    print("Making plot...")
    print("the game command was", game_command)
    # make_plot(all_results, all_errors, game_command, dir_name)
