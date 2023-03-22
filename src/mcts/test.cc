/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#include "core/state.h"
#include "games/connectfour.h"
#include "mcts.h"
#include "types.h"
#include "utils.h"

#include <algorithm>
#include <atomic>
#include <iomanip>
#include <iostream>
#include <random>

using namespace core;
using namespace mcts;
std::atomic<int> seed(0);


class TestActor : public core::Actor {
 public:
  // See src/core/actor.h and src/games/connectfour.h
  TestActor() : Actor(NULL, {3, 6, 7}, {7, 1, 1}, {}, 0, false, false, false, NULL) {
  }

  PiVal& evaluate(const State& s, PiVal& pival)  {
    const auto& state = dynamic_cast<const StateForConnectFour*>(&s);
    const auto& actions = state->GetLegalActions();
    std::vector<float> pi;
    pi.resize(actions.size());

    for (size_t i = 0; i < actions.size(); ++i) {
      pi[i] = 1.0 / actions.size();
    }
    auto player = state->getCurrentPlayer();
    float value = state->getRandomRolloutReward(state->getCurrentPlayer());
    pival = PiVal(player, value, std::move(pi));
    return pival;
  }
};


int main(int argc, char* argv[]) {
  // args are thread, rollouts
  assert(argc == 3);
  StateForConnectFour state(42);  // State(seed)
  state.Initialize();
  MctsOption option;
  // option.numThread = 2;
  option.numRolloutPerThread = std::stoi(std::string(argv[2]));
  option.puct = 1.0;
  option.virtualLoss = 1.0;
  std::vector<std::unique_ptr<MctsPlayer>> players;

  for (int i = 0; i < 2; ++i) {
    players.push_back(std::make_unique<MctsPlayer>(option));
    for (int j = 0; j < std::stoi(std::string(argv[1])); ++j) {
      players.at(i)->setActor(std::make_shared<TestActor>());
    }
  }

  int i = 0;
  while (!state.terminated()) {
    int playerIdx = state.getCurrentPlayer() == 1 ? 0 : 1;
    assert(!state.GetLegalActions().empty());
    state.printCurrentBoard();
    std::vector<_Action> theLegalActions = state.GetLegalActions();
    std::cout << "the legal actions are " << std::endl;
    for (_Action action : theLegalActions) {
      std::cout << "(" << action << ")" << std::endl;
    }
    std::cout << "before calling actMcts, the board was" << std::endl;
    state.printCurrentBoard();
    MctsResult result = players.at(playerIdx)->actMcts(state);
    std::cout << "after calling actMcts, the board was" << std::endl;
    state.printCurrentBoard();
    std::cout << "best action is that at index " << result.bestAction << std::endl;
    state.forward(result.bestAction);
    std::cout << "we took action " << theLegalActions[result.bestAction] << std::endl;
    std::cout << "now the board state is" << std::endl;
    state.printCurrentBoard();

    std::cout << "i " << i << std::endl;
    std::cout << "-----------" << std::endl;
    ++i;

    // if (i > 1) {
    //   break;
    // }
  }
  std::cout << "done!" << std::endl;
  state.printCurrentBoard();
  // std::cout << "winner is " << state.checkWinner() << std::endl;
  // assert(state.checkWinner() == 0);
  return 0;
}
