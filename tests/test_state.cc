/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#include "core/game.h"
#include "core/state.h"
#include <iostream>
#include <gtest/gtest.h>

float goodEval(core::State& s) {
  float numWins = 0;
  int gameCount = 0;
  while (gameCount < 100) {
    s.reset();
    while (!s.terminated()) {
      s.DoGoodAction();
    }
    numWins += 0.5 * (1 + s.getReward(0));
    ++gameCount;
  }
  float winRate = numWins / float(gameCount);
  std::cout << "good win rate = " << winRate << std::endl;
  if ((winRate <= 0.01) || (winRate >= 0.99)) {
    throw std::runtime_error(
        "this game has a random win rate beyond acceptable.");
  }
  return true;
}

float randEval(core::State& s) {
  float numWins = 0;
  int gameCount = 0;
  while (gameCount < 100) {
    s.reset();
    while (!s.terminated()) {
      s.DoRandomAction();
    }
    numWins += 0.5 * (1 + s.getReward(0));
    ++gameCount;
  }
  float winRate = numWins / float(gameCount);
  std::cout << "win rate = " << winRate << std::endl;
  if ((winRate <= 0.01) || (winRate >= 0.99)) {
    throw std::runtime_error(
        "this game has a random win rate beyond acceptable.");
  }
  return true;
}

int doSimpleTest(core::State& s) {
  // goodEval(s);
  // Test that everything is fine.
  // win_frequency = 0 or 1 in purely random play is weird.
  randEval(s);

  // Now testing if the game looks stochastic.
  bool isStochastic = false;
  // We will check this for various lengths of simulations, i is the length.
  // if isStochastic switches to true (i.e. a non-determinism is already
  // detected),
  // then we stop the loop.
  bool theoreticallyStochastic = s.isStochastic();
  for (int umax = 8; ((umax < 70) && (!isStochastic)); umax += 1) {
    s.Initialize();
    s.setSeed(5678);
    if (s.isStochastic()) {
      theoreticallyStochastic = true;
    }
    for (int u = 0; u < umax; u++) {
      if (!s.terminated())
        s.doIndexedAction(int(umax * 7.123 + u * 1.35));
      if (s.isStochastic()) {
        theoreticallyStochastic = true;
      }
      // s.stateDescription();
      // std::cout << "old:" << u << ":" << s.GetFeatures() << std::endl;
    }
    // std::cerr << s.stateDescription() << std::endl;
    auto oldFeatures = s.GetFeatures();
    // we play another game of length u.
    s.Initialize();
    s.setSeed(1234);
    for (int u = 0; u < umax; u++) {
      if (!s.terminated())
        s.doIndexedAction(int(umax * 7.123 + u * 1.35));
      // std::cout << "=====" << std::endl << s.stateDescription() << std::endl;
      // std::cout << "new:" << u << ":" << s.GetFeatures() << std::endl;
    }
    // std::cerr << s.stateDescription() << std::endl;
    if ((int)s.GetFeatures().size() != s.GetFeatureLength()) {
      throw std::runtime_error("wrong feature length");
    }
    for (int j = 0; ((!isStochastic) && (j < s.GetFeatureLength())); j++) {
      if (s.GetFeatures()[j] != oldFeatures[j]) {
        std::cout << "#horizon" << umax << "+feature" << j << "/"
                  << s.GetFeatureLength() << "--" << s.GetFeatures()[j]
                  << " vs " << oldFeatures[j] << std::endl;
        isStochastic = true;
      }
    }
    // if (isStochastic && (!theoreticallyStochastic)) {
    //   std::cout << "original:" << oldFeatures << std::endl;
    //   std::cout << "current: " << s.GetFeatures() << std::endl;
    // }
  }
  if (isStochastic != theoreticallyStochastic) {
    std::cout << s.stateDescription() << std::endl;
    std::cout << " Theoretically: " << theoreticallyStochastic << std::endl;
    std::cout << " Practically: " << isStochastic << std::endl;
    throw std::runtime_error("stochasticity violated");
  }
  // s.Initialize();
  return s.GetFeatureSize()[0];
}

void doTest(core::State& s) {
  s.copy(s); // check that _copyImpl is not null
  doSimpleTest(s);
  std::cout << "testing: fillFullFeatures at the end of ApplyAction and of "
               "Initialize."
            << std::endl;
  core::FeatureOptions opt;
  opt.randomFeatures = 3;
  s.setFeatures(&opt);
  doSimpleTest(s);
}


constexpr int seed = 999;
  TEST(StateTestsGroup, testTristannogo) {
    auto state = StateForTristannogo(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testBlockgo) {
    auto state = StateForBlockGo(seed);
    doTest(state);
  }
#ifndef NO_JAVA
  TEST(StateTestsGroup, testLudiiTicTacToe) {
    Ludii::JNIUtils::InitJVM("");  // Use default /ludii/Ludii.jar path
    JNIEnv* jni_env = Ludii::JNIUtils::GetEnv();
    assert(jni_env != nullptr);
      Ludii::LudiiGameWrapper game_wrapper("Tic-Tac-Toe.lud");
      auto state = std::make_unique<Ludii::LudiiStateWrapper>(
          seed, std::move(game_wrapper));
      doTest(*state);
      Ludii::JNIUtils::CloseJVM();
  }
#endif

  TEST(StateTestsGroup, testConnectFour) {
    auto state = StateForConnectFour(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testBreakthrough) {
    auto state = StateForBreakthrough(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testConnect6) {
    auto state = Connect6::StateForConnect6(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testTicTacToe) {
    auto state = MNKGame::State<3, 3, 3>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testFreestyleGomoku) {
    auto state = MNKGame::State<15, 15, 5>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testOthello8) {
    auto state8 = Othello::State<8>(seed);
    doTest(state8);
  }
  TEST(StateTestsGroup, testOthello10) {
    auto state10 = Othello::State<10>(seed);
    doTest(state10);
  }
  TEST(StateTestsGroup, testOthello16) {
    auto state16 = Othello::State<16>(seed);
    doTest(state16);
  }

  TEST(StateTestsGroup, testAmazons) {
    auto state = Amazons::State(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testChineseCheckers) {
    auto state = ChineseCheckers::State(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testGomokuSwap2) {  // Array index OOB error
    auto state = GomokuSwap2::State(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex5pie) {
    auto state = Hex::State<5, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex11pie) {
    auto state = Hex::State<11, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex13pie) {
    auto state = Hex::State<13, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex19pie) {
    auto state = Hex::State<19, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex5) {
    auto state = Hex::State<5, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex11) {
    auto state = Hex::State<11, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex13) {
    auto state = Hex::State<13, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHex19) {
    auto state = Hex::State<19, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testHavannah5pieExt) {
    auto state = Havannah::State<5, true, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testhavannah8pieExt) {
    auto state = Havannah::State<8, true, true>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testhavannah5pie) {
    auto state = Havannah::State<5, true, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testhavannah8pie) {
    auto state = Havannah::State<8, true, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testhavannah5) {
    auto state = Havannah::State<5, false, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testhavannah8) {
    auto state = Havannah::State<8, false, false>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testOuterOpenGomoku) {
    auto state = StateForOOGomoku(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testMastermind) {
    auto state = Mastermind::State<10, 7, 2>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testMinesweeperBeginner) {
    auto state = Minesweeper::State<8, 8, 10>(seed);
    doTest(state);
  }

  // win rates for intermediate and expert are too low
  // when taking random actions
  TEST(StateTestsGroup, DISABLED_testMinesweeperIntermediate) {
    auto state = Minesweeper::State<15, 13, 40>(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testMinesweeperExpert) {
    auto state = Minesweeper::State<30, 16, 99>(seed);
    doTest(state);
  }


  TEST(StateTestsGroup, testSurakarta) {
    auto state = StateForSurakarta(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testEinstein) {
    auto state = StateForEinstein(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testMinishogi) {  // Array index OOB error
    auto state = StateForMinishogi(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testDiceshogi) {  // Array index OOB error
    auto state = StateForDiceshogi(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testYinsh) {
    auto state = StateForYinsh(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, DISABLED_testKyotoshogi) {  // Array index OOB error
    auto state = StateForKyotoshogi(seed);
    doTest(state);
  }

  TEST(StateTestsGroup, testChess) {
    auto state = chess::State(seed);
    doTest(state);
  }
