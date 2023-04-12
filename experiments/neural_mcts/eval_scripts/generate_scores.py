import os
import pathlib
import sys


def make_command(model_path, opponent_path, save_dir):
    command_list = []
    command_list.append(f"python -m pypolygames eval")
    command_list.append(f"--checkpoint {model_path}")
    command_list.append(f"--num_game_eval 300")
    command_list.append(f"--num_rollouts_eval 1")
    command_list.append(f"--sample_before_step_idx 0")
    if mcts_opponent:
        num_rollouts = opponent_path.split("=")[1]
        command_list.append(f"--num_rollouts_opponent {num_rollouts}")
    if not mcts_opponent:
        command_list.append(f"--checkpoint_opponent {opponent_path}")
        command_list.append(f"--num_rollouts_opponent 1")
    # Save the output to out.txt and the error to err.txt
    command_list.append(f"2>> {save_dir}/err.txt")
    command_list.append(f">> {save_dir}/out.txt")
    command = " ".join(command_list)
    return command


if not len(sys.argv) == 4:
    print("Usage: python generate_scores.py checkpoint_path opponent_path save_dir")
    sys.exit()

_, checkpoint_dir, opponent_path, save_dir = sys.argv

if checkpoint_dir[-1] == "/":
    checkpoint_dir = checkpoint_dir[:-1]

if save_dir[-1] == "/":
    save_dir = save_dir[:-1]

if "MCTS" in opponent_path or "mcts" in opponent_path:
    assert "=" in opponent_path
    mcts_opponent = True
else:
    mcts_opponent = False

models = os.listdir(checkpoint_dir)
models = filter(lambda x: ".pt" in x, models)

# Remove the "out.txt" and the "model_names.txt" if they exist
for filename in ["out.txt", "err.txt", "model_names.txt", "command_history.txt"]:
    if os.path.isfile(f"{save_dir}/{filename}"):
        os.remove(f"{save_dir}/{filename}")
        print(f"removed old {save_dir}/{filename}")

# Make another file, in the same location as the "out.txt" fil,
# which contains the sys.argf from above
os.system(f"echo {sys.argv} >> {save_dir}/command_history.txt")

# Run the evals
for model in models:
    model_path = pathlib.Path(f"{checkpoint_dir}/{model}")
    command = str(make_command(model_path, opponent_path, save_dir))

    os.system(f"echo {model} >> {save_dir}/model_names.txt")
    os.system(f"echo 'running the following: \n {command}'")
    os.system(command)
