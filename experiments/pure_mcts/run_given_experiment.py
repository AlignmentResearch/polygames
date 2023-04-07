import shlex
import subprocess
import sys

from utils import make_plot


def run_games(num_games, all_commands, directory_path):
    all_results = []
    all_errors = []

    my_command = "blabla{seed}".format(seed=2)

    for game_command in all_commands:
        print("the command is: ", game_command)
        continue
        result = subprocess.run(
            game_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        result_string = result.stdout
        error_string = result.stderr

        all_results.append(result_string)
        all_errors.append(error_string)

    raise SystemExit

    # Save the results and the errors to files
    with open(f"{directory_path}/results.txt", "w") as f:
        f.writelines(all_results)
    with open(f"{directory_path}/errors.txt", "w") as f:
        f.writelines(all_errors)

    # Save the game command
    with open(f"{directory_path}/game_command.txt", "w") as f:
        f.writelines(' '.join(game_command))

    # Make the plot
    make_plot(all_results, all_errors, game_command, directory_path)


if __name__ == "__main__":
    game_command_path = sys.argv[1]
    all_commands = []
    firstline = True
    with open(game_command_path, "r") as f:
        for line in f:
            if firstline:
                firstline = False
                num_games = int(line)
            else:
                all_commands.append(shlex.split(line.strip()))

    # Strip the string "/game_command.txt" from the end of the path
    directory_path = game_command_path[:game_command_path.find("/game_command.txt")]

    run_games(num_games, all_commands, directory_path)