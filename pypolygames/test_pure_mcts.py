import subprocess

my_env = {"PYTHONPATH": "/polygames"}

num_bad = 0
for i in range(1000):
    if i % 10 == 0:
        print(i)
    result = subprocess.run(
        ["python", "-m", "pypolygames", "pure_mcts", "--game_name", "TicTacToe", "--seed", str(i)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=my_env,
    )

    if "the chosen action is" in result.stdout:
        print(result.stdout)
        break
        num_bad += 1
