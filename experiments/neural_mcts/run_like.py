import ast
import pathlib
import time
import subprocess
import sys

import pypolygames
import tube
import polygames
import mcts
import pypolygames.utils as utils

"""
This file is used to run a model with exactly the same hyperparameters as a given model.
"""


# Check to make sure we have exactly two arguments
if len(sys.argv) < 2:
    print("Usage: python run_like.py <path_to_model> <save_dir> <override_args>")
    sys.exit(1)

their_model_path_string = sys.argv[1]
save_dir_string = sys.argv[2]
override_args = sys.argv[3:]

# Parse the override args into key, value pairs
override_args_dict = {}
for arg in override_args:
    key, value = arg.split("=")
    override_args_dict[key] = value

# If the save_dir exists and isn't empty, ask the user if they would like to overwrite it
save_dir = pathlib.Path(save_dir_string)
if save_dir.exists() and len(list(save_dir.iterdir())) > 0:
    # overwrite = input(f"Save directory {save_dir_string} exists and is not empty. Overwrite? (y/n) ")
    # if overwrite != 'y':
    #     print("Exiting...")
    #     sys.exit(1)

    # Just overwrite it
    print("Overwriting the previous save directory at ", save_dir_string)

# If the save_dir doesn't exist, create it
if not save_dir.exists():
    save_dir.mkdir(parents=True)

their_model_path = pathlib.Path(their_model_path_string)
their_model = utils.load_checkpoint(their_model_path)

# Load in the model and copy over their parameters
param_group_names = ["game_params", "model_params", "optim_params", "simulation_params", "execution_params"]
not_used_for_training = ["time_ratio", "total_time"]
our_params = {}

# Parse in the (key, value) pairs from the model
for param_name in param_group_names:
    our_params[param_name] = {}
    their_param_group = their_model[param_name]
    # Add the key, value pairs to the command list.
    for key, value in their_param_group.__dict__.items():
        if key in override_args_dict:
            value = override_args_dict[key]
            del override_args_dict[key]
            print("Overriding", key, "with", value)
        our_params[param_name][key] = value
        print(f"added {param_name}.{key}: {value}")

# If there are any override args left, raise an error
if len(override_args_dict) > 0:
    raise ValueError(f"override args {override_args_dict} were not used. Exiting...")

# Remove the commands that should not be used in training
for param_group_name in param_group_names:
    for key in not_used_for_training:
        if key in our_params[param_group_name]:
            del our_params[param_group_name][key]

# If act_batchsize is nonzero and per_thread_batchsize is zero, remove per_thread_batchsize
if (
    our_params["simulation_params"]["act_batchsize"] != 0
    and our_params["simulation_params"]["per_thread_batchsize"] == 0
):
    print("Deleting per_thread_batchsize=0 because act_batchsize is nonzero")
    del our_params["simulation_params"]["per_thread_batchsize"]

# If act_batchsize is larger than num_game, set it to num_game
if int(our_params["simulation_params"]["act_batchsize"]) > int(our_params["simulation_params"]["num_game"]):
    print("Setting act_batchsize to num_game because act_batchsize is larger than num_game")
    our_params["simulation_params"]["act_batchsize"] = our_params["simulation_params"]["num_game"]

# Make the devices list into a CLI list
if "devices" in our_params["execution_params"]:
    # device_list = ast.literal_eval(our_params['execution_params']['devices']
    device_list = our_params["execution_params"]["devices"]
    print("the deice list is: ", our_params["execution_params"]["devices"])
    our_params["execution_params"]["device"] = ", ".join(device_list)
    print("now the device list is: ", our_params["execution_params"]["device"])

# Sanity check: do we have the things we need (TODO: make this more thorough)
if "nnks" not in our_params["model_params"]:
    print("hmm, no nnks in these model params, we should investigate")
    raise KeyError


def try_training():
    command_list = ["python", "-m", "pypolygames", "train"]
    for param_group_name in param_group_names:
        # Add the key, value pairs to the command list.
        # If the value is True, then we just add the key.
        # If the value is None, then we don't add the key or value.
        for key, value in our_params[param_group_name].items():
            if value is True:
                command_list.append(f"--{key}")
            elif value is not None and value is not False:
                command_list.append(f"--{key} {value}")

    command_list.append(f"--checkpoint_dir {save_dir_string}")
    command_list.append(f"> {save_dir_string}/stdout.txt")
    command_list.append(f"2> {save_dir_string}/stderr.txt")

    command = " ".join(command_list)

    print(f"running command: {command}")

    process = subprocess.Popen(command, shell=True)
    while process.poll() is None:
        time.sleep(1)

    print("---   done   ---")
    time.sleep(1)


try_training()
