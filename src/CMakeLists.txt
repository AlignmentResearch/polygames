include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(SYSTEM third_party)
include_directories(SYSTEM third_party/fmt/include)

add_subdirectory(third_party/fmt)
add_subdirectory(tube)
add_subdirectory(mcts)
add_subdirectory(games)
add_subdirectory(distributed)

file(GLOB _zstd_SOURCES third_party/zstd/lib/common/*.c third_party/zstd/lib/compress/*.c third_party/zstd/lib/decompress/*.c)
add_library(_zstd STATIC ${_zstd_SOURCES})

target_include_directories(_zstd BEFORE PUBLIC third_party/zstd/lib third_party/zstd/lib/common)

add_library(_common STATIC
  common/thread_id.cc
  common/threads.cc
  )

# This used to be SHARED, can still be built this way if the user wants to make C++ applications and not import pybind
add_library(_polygames STATIC
  core/game.cc
  core/state.cc
  core/replay_buffer.cc
  core/model_manager.cc
)

target_include_directories(_polygames SYSTEM PUBLIC ${PYTHON_INCLUDE_DIRS} ${TORCH_INCLUDE_DIRS})
target_link_libraries(_polygames PUBLIC
  _tube
  _mcts
  _games
  _distributed
  _common
  _zstd
  ${PYTHON_LIBRARIES}
  ${TORCH_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  )
pybind11_add_module(polygames MODULE
  core/pybind.cc
)
target_link_libraries(polygames PUBLIC _polygames)
