
#include "storage.h"

namespace mcts {

static std::mutex storagesMutex;
static std::vector<std::unique_ptr<Storage>> allStorages;
static std::vector<Storage*> freeStorages;


Node* Storage::newNode() {
  if (chunks_it == chunks.end()) {
    chunks.emplace_back();
    chunks_it = std::prev(chunks.end());

    chunks_it->reserve(CHUNK_SIZE);
    for (size_t i = 0; i < CHUNK_SIZE; ++i) {
      chunks_it->emplace_back(this);
    }
  }

  Node* r = &(*chunks_it)[subIndex];
  ++subIndex;
  if (subIndex == chunks_it->size()) {
    subIndex = 0;
    ++chunks_it;
  }

  ++allocated;
  return r;
}

void Storage::freeNode(Node* node) {
  assert(node->storage_ == this);

  --allocated;
  assert(allocated >= 0);
  if (allocated == 0) {
    chunks_it = chunks.begin();
    subIndex = 0;
    std::lock_guard l(storagesMutex);
    freeStorages.push_back(this);
  }
}

Storage* Storage::getStorage() {
  std::lock_guard l(storagesMutex);
  if (freeStorages.empty()) {
    allStorages.push_back(std::make_unique<Storage>());
    return allStorages.back().get();
  }
  Storage* r = freeStorages.back();
  freeStorages.pop_back();
  return r;
}

}  // namespace mcts
