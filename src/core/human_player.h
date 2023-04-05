/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#pragma once
#include "player.h"
#include "state.h"

namespace core {

class HumanPlayer : public Player {
 public:
  HumanPlayer() : Player(true){};
  virtual ~HumanPlayer(){};
};

class TPPlayer : public Player {
 public:
  TPPlayer() : Player(true) {isTP_ = true;};
  virtual ~TPPlayer(){};
};

}  // namespace core
