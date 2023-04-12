import matplotlib.pyplot as plt
import os
import sys

from utils import get_model_and_epoch, get_opponent_model_and_epoch, get_win_tie_loss_rates


assert len(sys.argv) == 3, "Usage: python make_plots.py eval_output_file plot_save_file"
_, eval_output_file, plot_save_file = sys.argv

with open(eval_output_file, "r") as afile:
    output = afile.read()


models_and_epochs, outlines, opponent = get_win_tie_loss_rates(output)

wins = []
ties = []
losses = []
for win, tie, loss in outlines:
    wins.append(win)
    ties.append(tie)
    losses.append(loss)

print("models and epochs")
print(models_and_epochs)

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

linestyles = [":", "--", "-.", "-", 1, 2, 3, 4, 5]
markerstyles = ["<", ">", "v", "^", 1, 2, 3, 4, 5]
print("all data", all_data)

for i, (model_type, data) in enumerate(all_data.items()):
    epochs = data["epoch"]
    wins = data["wins"]
    ties = data["ties"]
    losses = data["losses"]
    plt.plot(epochs, wins, markerstyles[i], color="g", linestyle=linestyles[i], label=f"{model_type}_win")
    plt.plot(epochs, ties, markerstyles[i], color="b", linestyle=linestyles[i], label=f"{model_type}_tie")
    plt.plot(epochs, losses, markerstyles[i], color="r", linestyle=linestyles[i], label=f"{model_type}_loss")

plt.title(f"Everyone against {opponent}")
plt.ylim(0, 100)
plt.legend()
plt.savefig(plot_save_file)
