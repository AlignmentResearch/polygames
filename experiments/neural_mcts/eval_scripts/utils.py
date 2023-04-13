import os
import pathlib
import sys


def make_command(model_path, num_pure_mcts_opponent_rollouts, save_dir) -> str:
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
