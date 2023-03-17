/**
 * Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#pragma once

#include "mcts/node.h"
#include <list>

namespace mcts {

static constexpr size_t CHUNK_SIZE = 128;

class Storage {
  std::vector<std::vector<Node> > chunks;
  int allocated = 0;
  std::vector<std::vector<Node> >::iterator chunks_it = chunks.begin();
  size_t subIndex = 0;

 public:
  Storage() = default;
  Storage(const Storage&) = delete;
  Storage& operator=(const Storage&) = delete;

  Node* newNode();
  void freeNode(Node* node);
  static Storage* getStorage();
};

}  // namespace mcts
