import matplotlib.pyplot as plt
import os
import sys

from old_make_plots import make_the_plot

# make the plot takes
# out.txt model_names.txt save_file.png plot_title


def make_many_plots(the_args):
    _, parent_directory, key_string = the_args

    out_filename = "out.txt"
    model_filename = "model_names.txt"

    # Search the directory structure for folders which contain the key string
    all_experiment_folders = sorted(
        [os.path.join(parent_directory, x) for x in os.listdir(parent_directory) if key_string in x]
    )

    for experiment_folder in all_experiment_folders:
        print("experiment folder", experiment_folder)

        # Get the out file and the model file in this folder
        out_file = os.path.join(experiment_folder, out_filename)
        model_file = os.path.join(experiment_folder, model_filename)

        # Make a title for the plot that we make
        plot_title = experiment_folder.split("/")[-1]

        # Make the plot
        make_the_plot(out_file, model_file, plot_title)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python make_plots.py parent_directory key_string")
        sys.exit()

    make_many_plots(sys.argv)
