/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#include "core/state.h"
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

class TicTacToeState : public State {
 public:
  TicTacToeState()
      : State(seed++) {
    board.clear();
    board.resize(9, 0);
    currentPlayer = 1;
    Initialize();
  }

  virtual void Initialize() override {
    currentPlayer = 1;
    this->_legalActions = getLegalActions();
    _actionSize = {(int)_legalActions.size(), 1, 1};
    _featSize = {9, 1, 1};
    _features.clear();
    _features.resize(_featSize[0] * _featSize[1] * _featSize[2]);
    std::fill(_features.begin(), _features.end(), 1.0f);
  }

  virtual std::unique_ptr<core::State> clone_() const override {
    return std::make_unique<TicTacToeState>(*this);
  }

  virtual void ApplyAction(const _Action& action) override {
    forward(action);
  }
  
  int getCurrentPlayer() const  {
    return currentPlayer;
  }

  uint64_t getHash() const  {
    return 0;
  }

  float getReward(int player) const  {
    int r = winner;
    if (r == 0)
      r = checkWinner();
    return r * player;
  };

  // bool isStochastic() const  {
  //   return false;
  // };

  std::vector<_Action> getLegalActions() const {  // so this is just seeing where hasn't been played yet
    std::vector<_Action> actions;
    for (int i = 0; i < 9; i++) {
      if (board.at(i) == 0) {
        _Action action(0, i, 0, 0);  // int index, int x, int y, int z
        actions.push_back(action);
      }
    }
    return actions;
  }

  float getRandomRolloutReward(int player) const  {
    int numRandomRollout = 100;
    int totalReward = 0;
    for (int i = 0; i < numRandomRollout; ++i) {
      TicTacToeState state;
      // std::cout << "start random rollout" << std::endl;
      // state.printState();
      state.board = board;
      state.currentPlayer = currentPlayer;
      state.moveIdx = moveIdx;
      while (!state.terminated()) {
        // state.printState();
        auto actions = state.getLegalActions();
        int idx = state.rng_() % actions.size();
        // std::cout << idx << "," << actions[idx] << ";;  ";
        state.forward(actions[idx]);
        // std::cout << "player " << player << ", action: "  << actions[idx] <<
        // std::endl;
        // state.printState();
      }
      // std::cout << "+++++++end of random rollout +++++++, winner: "
      //           << checkWinner() << std::endl;
      // state.winner = state.checkWinner();
      totalReward += state.checkWinner() * player;
    }
    return totalReward / (float)numRandomRollout;
  }

  bool operator==(const State&) const  {
    return false;
  }

  int getStepIdx() const  {
    return moveIdx;
  }

  std::unique_ptr<State> clone() const  {
    auto other = std::make_unique<TicTacToeState>();
    other->moveIdx = moveIdx;
    other->board = board;
    other->currentPlayer = currentPlayer;
    return other;
    // return std::make_unique<TicTacToeState>(other);
  }

  // const std::vector<mcts::Action>& getMoves() const  {
  //   return {};
  // }

  bool forward(const _Action& a)  {
    int ticTacToeMove = a.GetX();
    assert(ticTacToeMove >= 0 && ticTacToeMove <= 8);
    if (board[ticTacToeMove] != 0) {
      winner = -currentPlayer;
    }
    board[ticTacToeMove] = currentPlayer;
    currentPlayer = -currentPlayer;
    moveIdx += 1;
    return true;
  }

  bool forward(mcts::Action ticTacToeMove) {
    assert(ticTacToeMove >= 0 && ticTacToeMove <= 8);
    if (board[ticTacToeMove] != 0) {
      winner = -currentPlayer;
    }
    board[ticTacToeMove] = currentPlayer;
    currentPlayer = -currentPlayer;
    moveIdx += 1;
    return true;
  }

  bool terminated() const  {
    return winner != 0 || checkWinner() != 0 || moveIdx == 9;
  }

  int at(int i, int j) const {
    // std::cout << i << j << std::endl;
    assert(i >= 0 && i < 3 && j >= 0 && j < 3);
    return board[i * 3 + j];
  }

  void checkSum(int sum, int* winner) const {
    if (sum == 3)
      *winner = 1;
    if (sum == -3)
      *winner = -1;
  }

  int checkWinner() const {
    int w = 0;
    int sum = 0;
    for (int i = 0; i < 3; i++) {
      sum = 0;
      for (int j = 0; j < 3; j++) {
        sum += at(i, j);
        checkSum(sum, &w);
      }
      sum = 0;
      for (int j = 0; j < 3; j++) {
        sum += at(j, i);
        checkSum(sum, &w);
      }
    }
    sum = 0;
    for (int i = 0; i < 3; i++) {
      sum += at(i, i);
      checkSum(sum, &w);
    }
    sum = 0;
    for (int i = 0; i < 3; i++) {
      sum += at(i, 2 - i);
      checkSum(sum, &w);
    }
    return w;
  }

  void printState() {
    std::cout << "PRINT STATE===" << std::endl;
    std::cout << "current player is " << currentPlayer << std::endl;
    for (int i = 0; i < 9; ++i) {
      std::cout << std::setw(2);
      std::cout << board[i] << " ";
      if (i % 3 == 2) {
        std::cout << std::endl;
      }
    }
    // std::cout << std::endl;
  }

  std::vector<int> board;
  int currentPlayer = 1;
  int winner = 0;
  int moveIdx = 0;
  std::mt19937 rng_;
};

class TestActor : public core::Actor {
 public:
  // null, feature size, action size, empty, 0, ...
  TestActor() : Actor(NULL, {9, 1, 1}, {9, 1, 1}, {}, 0, false, false, false, NULL) {
    // TODO: understand above
  }

  PiVal& evaluate(const State& s, PiVal& pival)  {
    const auto& state = dynamic_cast<const TicTacToeState*>(&s);
    const auto& actions = state->getLegalActions();
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
  TicTacToeState state;
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
    MctsResult result = players.at(playerIdx)->actMcts(state);
    std::cout << "best action is " << result.bestAction << std::endl;
    state.forward(result.bestAction);
    state.printState();
    std::cout << "-----------" << std::endl;
    ++i;
    // if (i > 1) {
    //   break;
    // }
  }
  std::cout << "winner is " << state.checkWinner() << std::endl;
  assert(state.checkWinner() == 0);
  return 0;
}
