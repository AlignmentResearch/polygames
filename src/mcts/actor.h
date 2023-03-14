/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#pragma once

#include "core/actor.h"
#include "core/state.h"
#include "mcts/utils.h"

#include <functional>

namespace mcts {

// this is a minimal interface class,
// should ONLY keep functions used by mcts
class Actor {
 public:
  Actor() = default;

  Actor(const Actor&) = delete;
  Actor& operator=(const Actor&) = delete;

  virtual PiVal evaluate(const core::State& s) = 0;

  virtual ~Actor() {
  }

  virtual void evaluate(
      const std::vector<const core::State*>& s,
      const std::function<void(size_t, PiVal)>& resultCallback) {
    for (size_t i = 0; i != s.size(); ++i) {
      resultCallback(i, evaluate(*s[i]));
    }
  };

  virtual void terminate() {
  }

  virtual void recordMove(const core::State* state) {
  }

  virtual void result(const core::State* state, float reward) {
  }

  virtual bool isTournamentOpponent() const {
    return false;
  }
};

}  // namespace mcts
