# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, Tuple, Callable, Optional, List, Dict

import torch

import tube
import polygames
from pytube.data_channel_manager import DataChannelManager

from . import utils
from .params import GameParams, ModelParams, SimulationParams, ExecutionParams
from .env_creation_helpers import (
    sanitize_game_params,
    create_model,
    create_game,
    create_player,
)


#######################################################################################
# HUMAN-PLAYED ENVIRONMENT CREATION
#######################################################################################


def create_pure_mcts_environment(
    seed_generator: Iterator[int],
    game_params: GameParams,
    simulation_params: SimulationParams,
    execution_params: ExecutionParams,
    pure_mcts: bool,
    model
) -> Tuple[tube.Context, Optional[tube.DataChannel], Callable[[], int]]:
    human_first = execution_params.human_first
    time_ratio = execution_params.time_ratio
    total_time = execution_params.total_time
    context = tube.Context()
    actor_channel = (
        None if pure_mcts else tube.DataChannel("act", simulation_params.num_actor, 1)
    )
    rnn_state_shape = []
    if model is not None and hasattr(model, "rnn_cells") and model.rnn_cells > 0:
      rnn_state_shape = [model.rnn_cells, model.rnn_channels]
    rnn_state_size = 0
    if len(rnn_state_shape) >= 2:
      rnn_state_size = rnn_state_shape[0] * rnn_state_shape[1]
    logit_value = getattr(model, "logit_value", False)
    game = create_game(
        game_params,
        num_episode=1,
        seed=next(seed_generator),
        eval_mode=True,
        per_thread_batchsize=0,
        rewind=simulation_params.rewind,
        predict_end_state=game_params.predict_end_state,
        predict_n_states=game_params.predict_n_states,
    )
    player1 = create_player(
        seed_generator=seed_generator,
        game=game,
        player="mcts",
        num_actor=simulation_params.num_actor,
        # num_rollouts=simulation_params.num_rollouts,
        num_rollouts=0,
        pure_mcts=True,
        actor_channel=actor_channel,
        model_manager=None,
        human_mode=True,
        total_time=total_time,
        time_ratio=time_ratio,
        sample_before_step_idx=80,
        randomized_rollouts=False,
        sampling_mcts=False,
        rnn_state_shape=rnn_state_shape,
        rnn_seqlen=execution_params.rnn_seqlen,
        logit_value=logit_value,
    )
    player2 = create_player(
        seed_generator=seed_generator,
        game=game,
        player="mcts",
        num_actor=simulation_params.num_actor,
        # num_rollouts=simulation_params.num_rollouts,
        num_rollouts=100,
        pure_mcts=True,
        actor_channel=actor_channel,
        model_manager=None,
        human_mode=True,
        total_time=total_time,
        time_ratio=time_ratio,
        sample_before_step_idx=80,
        randomized_rollouts=False,
        sampling_mcts=False,
        rnn_state_shape=rnn_state_shape,
        rnn_seqlen=execution_params.rnn_seqlen,
        logit_value=logit_value,
    )
    game.add_eval_player(player1)
    game.add_eval_player(player2)

    context.push_env_thread(game)

    def get_result_for_human_player():
        nonlocal game, human_first
        return game.get_result()[not human_first]

    return context, actor_channel, get_result_for_human_player


#######################################################################################
# HUMAN-PLAYED GAME
#######################################################################################


def _play_game_against_mcts(context: tube.Context) -> None:
    context.start()
    while not context.terminated():
        time.sleep(1)


def play_game(
    pure_mcts: bool,
    devices: Optional[List[torch.device]],
    models: Optional[List[torch.jit.ScriptModule]],
    context: tube.Context,
    actor_channel: Optional[tube.DataChannel],
    get_result_for_human_player: Callable[[], int],
) -> int:
    _play_game_against_mcts(context)
    print("game over")
    return get_result_for_human_player()


#######################################################################################
# OVERALL HUMAN-PLAYED GAME WORKFLOW
#######################################################################################


def run_pure_mcts_played_game(
    game_params: GameParams,
    model_params: ModelParams,
    simulation_params: SimulationParams,
    execution_params: ExecutionParams,
):
    print("#" * 70)
    print("#" + "PURE-MCTS GAME".center(68) + "#")
    print("#" * 70)

    print("setting-up pseudo-random generator...")
    seed_generator = utils.generate_random_seeds(seed=execution_params.seed)

    devices, models = None, None

    model = None

    print("creating pure mcts environment")
    context, actor_channel, get_result_for_human_player = create_pure_mcts_environment(
        seed_generator=seed_generator,
        game_params=game_params,
        simulation_params=simulation_params,
        execution_params=execution_params,
        pure_mcts=model_params.pure_mcts,
        model=model
    )

    human_score = play_game(
        pure_mcts=model_params.pure_mcts,
        devices=devices,
        models=models,
        context=context,
        actor_channel=actor_channel,
        get_result_for_human_player=get_result_for_human_player,
    )

    print(f"result for the first player: {-human_score}")
