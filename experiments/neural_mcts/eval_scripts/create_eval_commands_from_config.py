import pathlib
import shlex
import sys

from run_eval_commands_from_files import generate_scores

"""
This script is used to generate the commands to run the evals for the
Neural MCTS checkpoints. It takes in the directory for all the models,
and the directory to save the evals to. It then creates a number of
new directories in the save_dir, each of which contains a command to
run (from a devbox) to actually do the evaluation.
"""

mcts_rollouts = [0, 32, 64, 128, 256, 512, 1024, 2048]
# mcts_rollouts = [256, 512, 1024, 2048]

container = 'ghcr.io/alignmentresearch/polygames:1.4.5-runner'


def run_against_several_MCTS_opponents(model_dir, save_dir, with_docker=True):
    for num_pure_mcts_opponent_rollouts in mcts_rollouts:
        if not with_docker:
            generate_scores(
                model_dir, num_pure_mcts_opponent_rollouts, save_dir + f"_vs_MCTS_{num_pure_mcts_opponent_rollouts}"
            )

        else:
            on_loki_command = ["ctl", "job", "run"]

            # Get the innermost director of the save dir path
            save_dir_name = pathlib.Path(save_dir).name

            on_loki_command += ["--name", f"{save_dir_name}-vs-mcts-{num_pure_mcts_opponent_rollouts}"]
            on_loki_command += ["--working-dir", "/polygames"]
            on_loki_command += ["--shared-host-dir-slow-tolerant"]
            on_loki_command += ["--container", f"{container}"]
            on_loki_command += ["--cpu", "4"]
            on_loki_command += ["--gpu", "1"]
            on_loki_command += ["--login"]
            on_loki_command += ["--wandb"]
            on_loki_command += ["--never-restart"]
            on_loki_command += ["--shared-host-dir", "/nas/ucb/k8"]
            on_loki_command += ["--shared-host-dir-mount", "/shared"]
            on_loki_command += ["--command", f"/bin/bash {save_dir}/run.sh"]

            single_command = shlex.join([
                f"python /polygames/experiments/neural_mcts/eval_scripts/generate_scores.py {model_dir} {num_pure_mcts_opponent_rollouts} {save_dir}",
            ])

            on_devbox_command = []
            on_devbox_command.append("cd /polygames")
            on_devbox_command.append("git checkout run_pure_mcts_experiments")
            on_devbox_command.append("git pull")
            on_devbox_command.append(single_command)
            with open(f"{save_dir}/run.sh", "w") as f:
                f.write("#!/bin/bash \n")

                # Just echo a hello to make sure it's running
                f.write('echo "found the script, now running it!" \n')

                # Now put all the commands in the file
                for command in on_devbox_command:
                    f.write(command + "\n")
            
            # Now run the job
            # subprocess.run(on_loki_command)
            # time.sleep(1)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python generate_scores.py checkpoint_path save_dir")
        sys.exit(1)
    _, model_dir, save_dir = sys.argv
    run_against_several_MCTS_opponents(model_dir, save_dir)
