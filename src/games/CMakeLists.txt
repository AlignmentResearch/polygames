cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

add_library(_games STATIC
  gomoku_swap2.cc
  othello_opt.cc
  mastermind_state.cc
  amazons.cc
  breakthrough.cc
  chess.cc
  chinesecheckers.cc
  tristan_nogo.cc
  yinsh.cc
  minesweeper.cc
  weakschur/SchurMatrix.cpp
  weakschur/SchurVector.cpp
  weakschur/WeakSchur.cpp)

if (JNI_FOUND)
  target_sources(_games PRIVATE
    ludii/jni_utils.cc
    ludii/ludii_game_wrapper.cc
    ludii/ludii_state_wrapper.cc)
  target_include_directories(_games SYSTEM PUBLIC ${JNI_INCLUDE_DIRS})
  target_link_libraries(_games PUBLIC ${JNI_LIBRARIES})
endif()

target_include_directories(_games PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_include_directories(_games SYSTEM PUBLIC
  ${TORCH_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS})
