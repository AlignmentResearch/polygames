# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, Tuple, Callable, Optional, List, Dict

import torch

import polygames.tube as tube
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
) -> Tuple[tube.Context, Optional[tube.DataChannel], Callable[[], int]]:
    human_first = execution_params.human_first
    actor_channel = None

    context = tube.Context()

    player_1_rollouts = simulation_params.num_rollouts
    player_2_rollouts = simulation_params.num_rollouts_2
    player_1_sample = simulation_params.sampling_mcts
    player_2_sample = simulation_params.sampling_mcts_2
    player_1_smooth = simulation_params.smooth_mcts_sampling
    player_2_smooth = simulation_params.smooth_mcts_sampling_2
    player_1_sample_before_step_idx = simulation_params.sample_before_step_idx
    player_2_sample_before_step_idx = simulation_params.sample_before_step_idx_2

    print("the important params are the following:")
    print("player_1_rollouts: ", player_1_rollouts)
    print("player_2_rollouts: ", player_2_rollouts)
    print("player_1_sample: ", player_1_sample)
    print("player_2_sample: ", player_2_sample)
    print("player_1_smooth: ", player_1_smooth)
    print("player_2_smooth: ", player_2_smooth)
    print("player_1_sample_before_step_idx: ", player_1_sample_before_step_idx)
    print("player_2_sample_before_step_idx: ", player_2_sample_before_step_idx)

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
        num_actor=1,
        num_rollouts=player_1_rollouts,
        pure_mcts=True,
        actor_channel=actor_channel,
        sample_before_step_idx=player_1_sample_before_step_idx,
        smooth_mcts_sampling=player_1_smooth,
        randomized_rollouts=player_1_sample,
        sampling_mcts=simulation_params.sampling_mcts,
    )
    player2 = create_player(
        seed_generator=seed_generator,
        game=game,
        player="mcts",
        num_actor=1,
        num_rollouts=player_2_rollouts,
        pure_mcts=True,
        actor_channel=actor_channel,
        sample_before_step_idx=player_2_sample_before_step_idx,
        smooth_mcts_sampling=player_2_smooth,
        randomized_rollouts=player_2_sample,
        sampling_mcts=simulation_params.sampling_mcts,
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


def run_pure_mcts_game(
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

    print("creating pure mcts environment")
    context, actor_channel, get_result_for_human_player = create_pure_mcts_environment(
        seed_generator=seed_generator,
        game_params=game_params,
        simulation_params=simulation_params,
        execution_params=execution_params,
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
