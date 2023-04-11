import re


def get_model_and_epoch(model_line):
    # the eval params are EvalParams(real_time=False, checkpoint_dir=None, 
    # checkpoint=PosixPath('/shared/polygames-parent/polygames-data/eval_scripts/../hex11pie/fb_checkpoints/Hex11pie_93_2019-09-29_DeepConvFCLogitModel_epoch22267_job18134581_6_208381bd.pt.gz'), 
    # device_eval=['cuda:0'], num_game_eval=500, num_parallel_games_eval=None, num_actor_eval=1, num_rollouts_eval=400, checkpoint_opponent=PosixPath('../hex11pie/fb_checkpoints/Hex11pie_89_2019-09-29_DeepConvFCLogitModel_epoch22016_job18134581_4_208381bd.pt.gz'), device_opponent=['cuda:0'], num_actor_opponent=1, num_rollouts_opponent=400, seed_eval=2, plot_enabled=False, plot_server='http://localhost', plot_port=8097, eval_verbosity=1)
    
    # Define a regular expression pattern to match the required information
    pattern = r'_([A-Za-z]+)_epoch(\d+)'

    # Use re.search() method to find the pattern in the string
    match = re.search(pattern, model_line)
    model_name = match.group(1)
    epoch_num = match.group(2)

    return model_name, int(epoch_num)


def get_opponent_model_and_epoch(model_line):
    pattern = r'_([A-Za-z]+)_epoch(\d+)'

    # Simply look in the correct place (vs making a more complicated regex)
    loc = model_line.find("checkpoint_opponent=")
    smaller_line = model_line[loc:]
    
    original_location = model_line.find(pattern)

    # Use re.search() method to find the pattern in the string
    match = re.search(pattern, model_line)
    model_name = match.group(1)
    epoch_num = match.group(2)

    return model_name, epoch_num


def get_win_tie_loss_rates(full_output_string):
    ##############
    # EVALUATION #
    ##############
    # blablabla
    # @@@eval: win: 94.00, tie: 0.00, loss: 6.00, avg: 94.00 blablabla
    # blablabla
    
    # First, need to divide into separate models. If a model failed, then we want to record "-1 -1 -1" for that model
    model_chunks = full_output_string.split("EVALUATION")[1:]  # we only care what's after the first "EVALUATION"
    split_chunks = [minichunk.split('\n') for minichunk in model_chunks]

    model_scores = []
    models_and_epochs = []
    opponent = None
    for chunk in split_chunks:
        for line in chunk:
            if "checkpoint=" in line:
                name, epoch = get_model_and_epoch(line)
                models_and_epochs.append((name, epoch))
                if opponent is None and "checkpoint_opponent=" in line:
                    opponent = get_opponent_model_and_epoch(line)
                continue
            if "@@@eval" in line:
                parts = line.split(' ')
                win = float(parts[2][:-1])
                tie = float(parts[4][:-1])
                loss = float(parts[6][:-1])
                model_scores.append((win, tie, loss))
                break
        else:
            model_scores.append((-1, -1, -1))

    return models_and_epochs, model_scores, opponent