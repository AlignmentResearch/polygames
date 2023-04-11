import os
import pathlib
import subprocess
import sys

mcts_rollouts = [0, 32, 64, 128, 256, 512, 1024, 2048]


def run_against_several_MCTS_opponents(model_dir, save_dir):
    for num_pure_mcts_opponent_rollouts in mcts_rollouts:
        generate_scores(
            model_dir, num_pure_mcts_opponent_rollouts, save_dir + f"_vs_MCTS_{num_pure_mcts_opponent_rollouts}"
        )


def make_command(model_path, num_pure_mcts_opponent_rollouts, save_dir):
    command_list = []
    command_list.append("python -m pypolygames eval")
    command_list.append(f"--checkpoint {model_path}")
    command_list.append("--num_game_eval 300")
    command_list.append("--num_rollouts_eval 0")
    command_list.append("--sample_before_step_idx 0")
    command_list.append(f"--num_rollouts_opponent {num_pure_mcts_opponent_rollouts}")
    # Save the output to out.txt and the error to err.txt
    command_list.append(f"2>> {save_dir}/err.txt")
    command_list.append(f">> {save_dir}/out.txt")
    command = " ".join(command_list)
    return command


def generate_scores(model_dir, num_pure_mcts_opponent_rollouts, save_dir):
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
        command = str(make_command(model_path, num_pure_mcts_opponent_rollouts, save_dir))

        subprocess.run(f"echo {model} >> {save_dir}/model_names.txt", shell=True)
        subprocess.run(f"echo 'running the following: \n {command}'", shell=True)
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python generate_scores.py checkpoint_path save_dir")
        sys.exit()
    _, model_dir, save_dir = sys.argv
    run_against_several_MCTS_opponents(model_dir, save_dir)
