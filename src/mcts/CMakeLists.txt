cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

add_library(_mcts STATIC
  node.cc
  mcts.cc
  storage.cc
)

target_include_directories(_mcts PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/..
  ${TORCH_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS})

target_link_libraries(_mcts PUBLIC
  pthread
  ${TORCH_LIBRARIES}
  $<TARGET_OBJECTS:_tube>
  )

# pybind lib
pybind11_add_module(mcts pybind.cc)
target_link_libraries(mcts PUBLIC libpolygames)
