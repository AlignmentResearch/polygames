import pathlib
import shlex
import sys

from generate_scores import generate_scores

"""
This script is used to generate the commands to run the evals for the
Neural MCTS checkpoints. It takes in the directory for all the models,
and the directory to save the evals to. It then creates a number of
new directories in the save_dir, each of which contains a command to
run (from a devbox) to actually do the evaluation.
"""

CONTAINER = "ghcr.io/alignmentresearch/polygames:1.4.8-runner"
CURRENT_BRANCH = "run_neural_evals"
MCTS_ROLLOUTS = [256, 1024, 4096, 8192]


def run_against_several_MCTS_opponents(model_dir, save_dir, with_docker=True):
    for num_pure_mcts_opponent_rollouts in MCTS_ROLLOUTS:
        if not with_docker:
            generate_scores(
                model_dir, num_pure_mcts_opponent_rollouts, save_dir + f"_vs_MCTS_{num_pure_mcts_opponent_rollouts}"
            )

        else:
            on_loki_command = ["ctl", "job", "run"]

            # Get the innermost director of the save dir path
            save_dir_name = pathlib.Path(save_dir).name

            # Make a directory for this specific number of MCTS rollouts
            # Put it inside the save dir
            specific_save_dir = save_dir + f"model_vs_MCTS_{num_pure_mcts_opponent_rollouts}"
            pathlib.Path(specific_save_dir).mkdir(parents=True, exist_ok=True)

            on_loki_command += ["--name", f"{save_dir_name}-vs-mcts-{num_pure_mcts_opponent_rollouts}"]
            on_loki_command += ["--working-dir", "/polygames"]
            on_loki_command += ["--shared-host-dir-slow-tolerant"]
            on_loki_command += ["--container", f"{CONTAINER}"]
            on_loki_command += ["--cpu", "16"]
            on_loki_command += ["--gpu", "1"]
            on_loki_command += ["--login"]
            # on_loki_command += ["--wandb"]
            on_loki_command += ["--never-restart"]
            on_loki_command += ["--shared-host-dir", "/nas/ucb/k8"]
            on_loki_command += ["--shared-host-dir-mount", "/shared"]
            on_loki_command += ["--command", f"/bin/bash {specific_save_dir}/run.sh"]

            single_command = f"python /polygames/experiments/neural_mcts/eval_scripts/generate_scores.py {model_dir} {num_pure_mcts_opponent_rollouts} {specific_save_dir}"

            # Save the command to run the container itself
            with open(f"{specific_save_dir}/docker_command.txt", "w") as f:
                f.write(shlex.join(on_loki_command))
            print("just wrote to the following file: ", f"{specific_save_dir}/docker_command.txt")

            # Save the command to run from within the container
            with open(f"{specific_save_dir}/run.sh", "w") as f:
                f.write("#!/bin/bash \n")

                # Just echo a hello to make sure it's running
                f.write('echo "found the script, now running it!" \n')

                # Now put all the commands in the file
                on_devbox_command = []
                on_devbox_command.append('echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf')  # for internet access
                on_devbox_command.append("cd /polygames")
                on_devbox_command.append("git remote set-url origin https://github.com/AlignmentResearch/polygames.git")
                on_devbox_command.append("git fetch")
                on_devbox_command.append(f"git checkout {CURRENT_BRANCH}")
                on_devbox_command.append(f"git branch --set-upstream-to=origin/{CURRENT_BRANCH} {CURRENT_BRANCH}")
                on_devbox_command.append("git pull")
                on_devbox_command.append(f"(time {single_command}) > {specific_save_dir}/time.log")
                for command in on_devbox_command:
                    f.write(command + "\n")

            print("just wrote to the following file: ", f"{specific_save_dir}/run.sh")

            # Now run the job
            # subprocess.run(on_loki_command)
            # time.sleep(1)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python create_eval_commands_from_dir.py model_dir save_dir")
        sys.exit(1)
    _, model_dir, save_dir = sys.argv
    run_against_several_MCTS_opponents(model_dir, save_dir)
