import matplotlib.pyplot as plt
import os
import sys


def get_model_and_epoch(model_line):
    # 'Hex5pie_85_2019-09-27_ResConvConvLogitModel_epoch10246_job18105640_51_8faf6f73.pt.gz'
    parts = model_line.split("_")
    if len(parts) == 1:
        return "checkpoint", 0
    if len(parts) == 2:
        return parts[0], int(parts[1][:-3])
    elif len(parts) <= 5:
        print("hmm, this checkpoint doesn't have the kind of name I expected")
        print(model_line)
        raise ValueError
    else:
        name = parts[3]
        epoch = int(parts[4][5:])
        return name, epoch


def get_win_tie_loss_rates(full_output_string):
    ##############
    # EVALUATION #
    ##############
    # blablabla
    # @@@eval: win: 94.00, tie: 0.00, loss: 6.00, avg: 94.00 blablabla
    # blablabla

    # First, need to divide into separate models. If a model failed, then we want to record "-1 -1 -1" for that model
    model_chunks = full_output_string.split("EVALUATION")[1:]  # we only care what's after the first "EVALUATION"
    split_chunks = [minichunk.split("\n") for minichunk in model_chunks]

    model_scores = []
    for chunk in split_chunks:
        for line in chunk:
            if "@@@eval" in line:
                parts = line.split(" ")
                win = float(parts[2][:-1])
                tie = float(parts[4][:-1])
                loss = float(parts[6][:-1])
                model_scores.append((win, tie, loss))
                break
        else:
            model_scores.append((-1, -1, -1))

    return model_scores


def make_the_plot(eval_output_file, model_names_file, plot_save_file, plot_title):
    with open(eval_output_file, "r") as afile:
        output = afile.read()

    with open(model_names_file, "r") as afile:
        model_names = afile.read().strip().split("\n")

    outlines = get_win_tie_loss_rates(output)

    models_and_epochs = []
    for model_line in model_names:
        models_and_epochs.append(get_model_and_epoch(model_line))

    wins = []
    ties = []
    losses = []
    for win, tie, loss in outlines:
        wins.append(win)
        ties.append(tie)
        losses.append(loss)

    # Sort each of the models according to model type
    unique_model_types = set([model_type for model_type, epoch in models_and_epochs])

    # Collect the epoch, wins, ties and losses, and sort them by model type
    all_data = {}
    for model_type in unique_model_types:
        all_data[model_type] = {"epoch": [], "wins": [], "ties": [], "losses": []}
        for i, (current_model_type, epoch) in enumerate(models_and_epochs):
            if current_model_type == model_type and wins[i] != -1:
                all_data[model_type]["epoch"].append(epoch)
                all_data[model_type]["wins"].append(wins[i])
                all_data[model_type]["ties"].append(ties[i])
                all_data[model_type]["losses"].append(losses[i])
        # Now sort those data
        sorted_data = {
            k: [v for _, v in sorted(zip(all_data[model_type]["epoch"], all_data[model_type][k]))]
            for k in all_data[model_type].keys()
        }
        all_data[model_type] = sorted_data

    linestyles = [":", "--", "-.", "-"]
    markerstyles = ["<", ">", "v", "^"]
    print("all data", all_data)

    for i, (model_type, data) in enumerate(all_data.items()):
        epochs = data["epoch"]
        wins = data["wins"]
        ties = data["ties"]
        losses = data["losses"]
        plt.plot(epochs, wins, markerstyles[i], color="g", linestyle=linestyles[i], label=f"{model_type}_win")
        plt.plot(epochs, ties, markerstyles[i], color="b", linestyle=linestyles[i], label=f"{model_type}_tie")
        plt.plot(epochs, losses, markerstyles[i], color="r", linestyle=linestyles[i], label=f"{model_type}_loss")

    plt.title(plot_title)
    plt.ylim(0, 100)
    plt.grid()
    plt.legend()
    plt.savefig(plot_save_file)
    plt.close()


if __name__ == "__main__":
    if not len(sys.argv) == 5:
        print("Usage: python make_plots.py out.txt model_names.txt save_file.png plot_title")
        sys.exit()

    make_the_plot(*sys.argv[1:])
