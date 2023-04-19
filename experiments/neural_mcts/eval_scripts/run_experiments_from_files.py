import os
import shlex
import subprocess
import sys


def get_docker_commands_from_directories(root_directory):
    # There will be a number of directories which have a file called "docker_command.txt" in them,
    # off of the root directory. For each of those files, run "run_from_command_line_inputs" on the
    # command in the file.

    for item in sorted(os.scandir(root_directory), key=lambda x: x.name.lower()):
        if item.is_dir():
            directory_path = item.path
            docker_command_file = os.path.join(directory_path, "docker_command.txt")
            if os.path.isfile(docker_command_file):
                with open(docker_command_file, "r") as f:
                    docker_command = f.readlines()[0].strip()
                print(f"Running {docker_command}...")
                subprocess.run(shlex.split(docker_command))
        elif item.is_file() and item.name == "docker_command.txt":
            with open(item.path, "r") as f:
                docker_command = f.readlines()[0].strip()
            print(f"Running {docker_command}...")
            subprocess.run(shlex.split(docker_command))
        else:
            print(f"Skipping {item} because it doesn't have a docker_command.txt file")


if __name__ == "__main__":
    # Take the root directory and run the thing we want
    root_directory = sys.argv[1]
    get_docker_commands_from_directories(root_directory)
