import os
import pathlib
import subprocess
import sys

from utils import make_command


def generate_scores(model_dir, num_pure_mcts_opponent_rollouts, save_dir):
    # Get us to the correct git repo
    subprocess.run("cd /polygames", shell=True)
    subprocess.run("git checkout run_pure_mcts_experiments", shell=True)
    subprocess.run("git pull", shell=True)

    if model_dir[-1] == "/":
        model_dir = model_dir[:-1]

    if save_dir[-1] == "/":
        save_dir = save_dir[:-1]

    models = sorted(os.listdir(model_dir))
    models = filter(lambda x: ".pt" in x, models)

    # If the save dir doesn't exist, then make it
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    else:
        # Remove the "out.txt" and the "model_names.txt" if they exist
        for filename in ["out.txt", "err.txt", "model_names.txt", "command_history.txt"]:
            if os.path.isfile(f"{save_dir}/{filename}"):
                os.remove(f"{save_dir}/{filename}")
                print(f"removed old {save_dir}/{filename}")

    # Make another file, in the same location as the "out.txt" fil,
    # which contains the sys.argf from above
    subprocess.run(f"echo {sys.argv} >> {save_dir}/command_history.txt", shell=True)

    # Run the evals
    for model in models:
        model_path = pathlib.Path(f"{model_dir}/{model}")
        command = make_command(model_path, num_pure_mcts_opponent_rollouts, save_dir)

        subprocess.run(f"echo {model} >> {save_dir}/model_names.txt", shell=True)
        subprocess.run(f"echo 'running the following: \n {command}'", shell=True)
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print("Usage: generate_scores model_dir num_pure_mcts_opponent_rollouts save_dir")
        sys.exit(1)

    _, model_dir, num_pure_mcts_opponent_rollouts, save_dir = sys.argv

    # Check whether the model dir and save dir exist
    if not os.path.isdir(model_dir):
        print(f"model_dir {model_dir} does not exist")
        sys.exit(1)
    if not os.path.isdir(save_dir):
        print(f"save_dir {save_dir} does not exist, so we'll make it")
        os.mkdir(save_dir)

    generate_scores(model_dir, num_pure_mcts_opponent_rollouts, save_dir)
