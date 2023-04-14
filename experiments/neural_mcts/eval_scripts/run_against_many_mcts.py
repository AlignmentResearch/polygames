import pathlib
import time
import subprocess
import sys

from generate_scores import generate_scores

mcts_rollouts = [0, 32, 64, 128, 256, 512, 1024, 2048]
# mcts_rollouts = [256, 512, 1024, 2048]


def run_against_several_MCTS_opponents(model_dir, save_dir, with_docker=True):
    for num_pure_mcts_opponent_rollouts in mcts_rollouts:
        if not with_docker:
            generate_scores(
                model_dir, num_pure_mcts_opponent_rollouts, save_dir + f"_vs_MCTS_{num_pure_mcts_opponent_rollouts}"
            )

        else:
            docker_command = ["ctl", "job", "run"]

            # Get the innermost director of the save dir path
            save_dir_name = pathlib.Path(save_dir).name

            docker_command += ["--name", f"{save_dir_name}-vs-mcts-{num_pure_mcts_opponent_rollouts}"]
            docker_command += ["--working-dir", "/polygames"]
            docker_command += ["--shared-host-dir-slow-tolerant"]
            docker_command += ["--container", "ghcr.io/alignmentresearch/polygames:1.4.5-runner"]
            docker_command += ["--cpu", "4"]
            docker_command += ["--gpu", "1"]
            docker_command += ["--login"]
            docker_command += ["--wandb"]
            docker_command += ["--never-restart"]
            docker_command += ["--shared-host-dir", "/nas/ucb/k8"]
            docker_command += ["--shared-host-dir-mount", "/shared"]
            docker_command += [
                "--command",
                f"python" "/polygames/experiments/neural_mcts/eval_scripts/generate_scores.py",
                f"{model_dir}",
                f"{num_pure_mcts_opponent_rollouts}",
                f"{save_dir}",
            ]

            # Now run the job
            subprocess.run(docker_command)

            time.sleep(1)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python generate_scores.py checkpoint_path save_dir")
        sys.exit(1)
    _, model_dir, save_dir = sys.argv
    run_against_several_MCTS_opponents(model_dir, save_dir)
