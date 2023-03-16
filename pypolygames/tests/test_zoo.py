# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from unittest import SkipTest
import pytest
import torch
import torch.nn.functional as F
from .. import model_zoo
from ..model_zoo.utils import get_game_info
from .. import params
from .. import utils

# NOTE: Copied this loss from a model in the first commit
def loss(
    model,
    x: torch.Tensor,
    v: torch.Tensor,
    pi: torch.Tensor,
    pi_mask: torch.Tensor,
    stat: utils.MultiCounter,
) -> float:
    pi = pi.flatten(1)
    pred_v, pred_logit = model._forward(x, True)
    utils.assert_eq(v.size(), pred_v.size())
    utils.assert_eq(pred_logit.size(), pi.size())
    utils.assert_eq(pred_logit.dim(), 2)

    pred_logit = pred_logit * pi_mask.view(pred_logit.shape)

    v_err = 0.5 * (v - pred_v).pow(2).squeeze(1)
    s = pred_logit.shape
    bs = x.shape[0]
    pred_log_pi = F.log_softmax(pred_logit.flatten(1), 1).reshape(s)
    pi_err = -(pred_log_pi * pi).sum(1)

    utils.assert_eq(v_err.size(), pi_err.size())
    err = v_err + pi_err

    stat["v_err"].feed(v_err.detach().mean().item())
    stat["pi_err"].feed(pi_err.detach().mean().item())
    return err.mean()


@pytest.mark.parametrize("model_name", [n for n in model_zoo.MODELS])
def test_models(model_name) -> None:
    if model_name in ["Connect4BenchModel", "ResConvConvLogitPoolModelV2"]:
        raise SkipTest(f"Skipping {model_name}")
    game_params = params.GameParams(
        game_name="Tristannogo"
        if "GameOfTheAmazons" not in model_name
        else "GameOfTheAmazons"
    )
    model_params = params.ModelParams(model_name=model_name)
    info = get_game_info(game_params)
    model = model_zoo.MODELS[model_name](game_params, model_params)
    model.eval()  # necessary for batch norm as it expects more than 1 ex in training
    feature_size = info["feature_size"][:3]
    action_size = info["action_size"][:3]
    input_data = torch.zeros([1] + feature_size, device=torch.device("cpu"))
    outputs = model.forward(input_data)
    assert list(outputs["v"].shape) == [1, 1]
    assert list(outputs["pi_logit"].shape) == [1] + action_size
    # loss
    multi_counter = utils.MultiCounter(root=None)
    pi_mask = torch.ones(outputs["pi_logit"].shape)
    loss(
        model, input_data, outputs["v"], outputs["pi_logit"], pi_mask, multi_counter
    )  # make sure it computes something
