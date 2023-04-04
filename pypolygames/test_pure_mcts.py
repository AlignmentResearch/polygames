import subprocess

my_env = {"PYTHONPATH": "/polygames"}

num_bad = 0
for i in range(100):
    game_command = ['python', '-m', 'pypolygames', 'pure_mcts', 
                    '--game_name', 'TicTacToe', '--seed', str(i)]

    # game_command += ['--sampling_mcts', 'True']

    result = subprocess.run(
        game_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=my_env,
    )

    result_string = result.stdout
    result_list = result_string.splitlines()
    result_line = result_list[6]

    # result_location = result.stdout.find("player") + len("player") + 2
        # if "result for the first player" in line:
    print(i, result_line)
