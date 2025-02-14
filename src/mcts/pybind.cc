/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#include "pybind.h"
#include "mcts.h"

namespace py = pybind11;

namespace mcts {
void pybind_submodule(py::module &m) {
  py::class_<MctsPlayer, core::ActorPlayer, std::shared_ptr<MctsPlayer>>(
      m, "MctsPlayer")
      .def(py::init<const MctsOption&>(),
           py::call_guard<py::gil_scoped_release>());

  py::class_<MctsOption>(m, "MctsOption")
      .def(py::init<>())
      .def(py::init<const MctsOption&>())
      .def_readwrite("puct", &MctsOption::puct)
      .def_readwrite("sample_before_step_idx", &MctsOption::sampleBeforeStepIdx)
      .def_readwrite("smooth_mcts_sampling", &MctsOption::smoothMctsSampling)
      .def_readwrite("num_rollout_per_thread", &MctsOption::numRolloutPerThread)
      .def_readwrite("seed", &MctsOption::seed)
      .def_readwrite("virtual_loss", &MctsOption::virtualLoss)
      .def_readwrite("store_state_interval", &MctsOption::storeStateInterval)
      .def_readwrite("use_value_prior", &MctsOption::useValuePrior)
      .def_readwrite("time_ratio", &MctsOption::timeRatio)
      .def_readwrite("total_time", &MctsOption::totalTime)
      .def_readwrite("randomized_rollouts", &MctsOption::randomizedRollouts)
      .def_readwrite("sampling_mcts", &MctsOption::samplingMcts)
      .def_readwrite(
          "forced_rollouts_multiplier", &MctsOption::forcedRolloutsMultiplier);
}

} // namespace mcts
