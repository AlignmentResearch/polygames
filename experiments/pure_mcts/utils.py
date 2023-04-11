import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import shlex


def make_plot(all_results: list[str], all_errors: list[str], game_command: list[str], save_directory: str) -> None:
    indices = []
    results = []
    unlikely_move_occurred = []
    i = 0
    for result_string in all_results:
        # splitlines gives (idx, line)
        for line in result_string.splitlines():
            if "result for the first player" in line:
                # could be " 1.0" or "-1.0" or " 0.0" or "-0.0"
                results.append(float(line[-4:]))
                unlikely_move_occurred.append(0)
                indices.append(i)
                i += 1

            if "Black" in line:
                unlikely_move_occurred[i - 1] += 1  # indexing here is hacky

    print("the indices are", indices)
    print("the results are", results)
    print("the unlikely move occurred are", unlikely_move_occurred)
    print()

    # create a pandas DataFrame from the data
    df = pd.DataFrame({"win_tie_loss": results, "weird": unlikely_move_occurred})

    # create the contingency table with margins
    table = pd.crosstab(df["win_tie_loss"], df["weird"], margins=True)

    # print the table
    print(table)
    print()

    # create the contingency table with margins and normalize by rows
    table_norm_rows = pd.crosstab(df["win_tie_loss"], df["weird"], margins=True, normalize="index")
    print(table_norm_rows)
    print()

    # create the contingency table with margins and normalize by columns
    table_norm_cols = pd.crosstab(df["win_tie_loss"], df["weird"], margins=True, normalize="columns")
    print(table_norm_cols)

    # create a 1x2 grid of subplots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, gridspec_kw={"width_ratios": [2, 1]})

    # create a heatmap of the contingency table on ax1
    heatmap = sns.heatmap(
        table, cmap="YlGnBu", annot=True, fmt="d", cbar=False, linewidths=0, linecolor="white", ax=ax1
    )

    # remove the left and top spines
    sns.despine(left=True, top=True, right=True, bottom=True)

    # add horizontal lines to separate the marginal distributions
    heatmap.hlines([0, table.shape[0] - 1], 0, table.shape[1], colors="black", linewidths=2)

    # add vertical lines to separate the marginal distributions
    heatmap.vlines([0, table.shape[1] - 1], 0, table.shape[0], colors="black", linewidths=2)

    # add axis labels and title to ax1
    ax1.set_xlabel("Weird")
    ax1.set_ylabel("Win/Tie/Loss")
    ax1.set_title("")

    # Get the stats
    commands = []
    i = 0  # don't care about the "python" bit
    while i < len(game_command) - 2:  # don't care about the seed
        commands.append(" ".join(game_command[i : i + 2]))
        i += 2

    text = "\n".join(commands)
    ax2.text(0.1, 0.5, text, va="center", fontsize=8)

    # remove ticks and spines from ax2
    ax2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    sns.despine(ax=ax2, left=True, top=True, right=True, bottom=True)

    # adjust the figure size
    plt.gcf().set_size_inches(4, 2)

    # save the plot to a PDF file
    plt.savefig(f"{save_directory}/contingency_table.pdf", dpi=100, bbox_inches="tight")

    # plt.plot(indices, results, 'o', label="results")
    # plt.plot(indices, unlikely_move_occurred, 'o', label="# unlikely moves in this game")

    # plt.legend()
    # plt.grid()
    # plt.savefig("results.png")


def get_results_from_directory(directory_name):
    all_results_file = f"{directory_name}/results.txt"
    with open(all_results_file, "r") as f:
        all_results = f.readlines()
    all_errors_file = f"{directory_name}/errors.txt"
    with open(all_errors_file, "r") as f:
        all_errors = f.readlines()
    game_command_file = f"{directory_name}/game_command.txt"
    with open(game_command_file, "r") as f:
        game_command = f.readlines()[0].split(" ")

    return all_results, all_errors, game_command
