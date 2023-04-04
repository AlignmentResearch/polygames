cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

add_library(_mcts STATIC
  node.cc
  mcts.cc
  storage.cc
  pybind.cc
)

target_include_directories(_mcts PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_include_directories(_mcts SYSTEM PUBLIC
  ${TORCH_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS})
target_link_libraries(_mcts PUBLIC
  pthread
  ${TORCH_LIBRARIES}
  _polygames
)
# We don't add the pybind11 module on purpose -- let `libpolygames` link all of it.
# pybind11_add_module(mcts pybind.cc)
