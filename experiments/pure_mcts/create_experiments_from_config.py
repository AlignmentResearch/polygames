from __future__ import annotations
import os
import shlex
import sys
import yaml

from utils import make_directory_name_from_command


DEFAULT_NUMBER_OF_GAMES = 100
EXPERIMENTS_DIRECTORY = "/shared/polygames-parent/experiments/pure_mcts"
CURRENT_BRANCH = "run_pure_mcts_experiments"


def setup_game_and_save_command(
    game_name: str, num_rollouts: int, num_rollouts_2: int, num_games: int, hparams: dict, save_plots: bool = True
) -> None:
    game_command = []
    for key, value in hparams.items():
        if key == "game_name":
            game_command += ["--" + key, game_name]
        elif key == "num_rollouts":
            game_command += ["--" + key, str(num_rollouts)]
        elif key == "num_rollouts_2":
            game_command += ["--" + key, str(num_rollouts_2)]
        else:
            game_command += ["--" + key, str(value)]

    dir_name = make_directory_name_from_command(game_command, num_games)
    directory_path = f"{EXPERIMENTS_DIRECTORY}/{dir_name}"

    container = "ghcr.io/alignmentresearch/polygames:1.4.6-runner"

    single_command = (
        f"python /polygames/experiments/pure_mcts/run_given_experiment.py "
        f"{shlex.join(game_command)} --SPECIAL_num_games {num_games} "
        f"--SPECIAL_save_plots {save_plots} --SPECIAL_directory_path {directory_path}"
    )

    # For testing
    # subprocess.run(shlex.split(single_command))

    experiment_name = make_directory_name_from_command(game_command, num_games, hyphenated=True, shorten=True)

    print("experiment name:", experiment_name, "length:", len(experiment_name))

    # The docker command runs `run.sh`, which we create from the `commands` variable below.
    docker_command = (
        f'ctl job run --name "nhowe-{experiment_name}" --working-dir /polygames '
        f'--shared-host-dir-slow-tolerant --container "{container}" --cpu 4 --gpu 1 '
        "--login --never-restart --shared-host-dir /nas/ucb/k8 --shared-host-dir-mount /shared "
        f'--command "/bin/bash {directory_path}/run.sh"'
    )

    # If the directory doesn't exist yet, create it
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Also write these commands to a bash script that can be run
    commands = []
    commands.append('echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf')  # for internet access
    commands.append("git remote set-url origin https://github.com/AlignmentResearch/polygames.git")
    commands.append("git branch --set-upstream-to=origin/run_pure_mcts_experiments run_pure_mcts_experiments")
    commands.append("git pull")
    commands.append(f"git checkout {CURRENT_BRANCH}")
    commands.append(single_command)
    with open(f"{directory_path}/run.sh", "w") as f:
        f.write("#!/bin/bash \n")

        # Just echo a hello to make sure it's running
        f.write('echo "hello, we got to the bash script" \n')

        # Now put all the commands in
        for command in commands:
            f.write(command + "\n")

    # Make the file executable
    os.chmod(f"{directory_path}/run.sh", 0o755)

    # Print the command
    print("about to write this command to disk (but not running it)")
    print(docker_command)
    print("it will be saved to", f"{directory_path}/docker_command.txt")

    # Save the command to a file in the desired directory
    with open(f"{directory_path}/docker_command.txt", "w") as f:
        f.write(docker_command)

    print("wrote the command to disk \n")

    # Ideally, we would like to just do the following, instead of writing the
    # command and then calling it from loki. Unfortunately, I haven't been
    # able to get that to work properly, so the two-step process
    # is a workaround for now.
    # subprocess.run(shlex.split(docker_command))


def run_games(num_games: int, save_plots: bool = True) -> None:
    # Get the directory containing the yaml file
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)

    with open(f"{current_dir}/config.yaml", "r") as f:
        hyperparameters = yaml.load(f, Loader=yaml.FullLoader)

    for game_name in hyperparameters["game_name"]:
        # Actually, we only want to play everything against the strongest,
        # and the strongest against everything
        max_rollouts = max(hyperparameters["num_rollouts"])

        for num_rollouts in hyperparameters["num_rollouts"]:
            # Set all the hyperparameters, fixing the values of the ones
            # we've already set

            setup_game_and_save_command(game_name, num_rollouts, max_rollouts, num_games, hyperparameters)
            setup_game_and_save_command(game_name, max_rollouts, num_rollouts, num_games, hyperparameters)


if __name__ == "__main__":
    print(f"Running default number of games ({DEFAULT_NUMBER_OF_GAMES})...")
    run_games(DEFAULT_NUMBER_OF_GAMES)
