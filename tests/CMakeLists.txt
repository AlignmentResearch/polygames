include_directories(
../src
 ../src/games
 ../src/games/weakschur
 ../src/third_party
 ../src/third_party/fmt/include
 ../src/tube/src_cpp
 ../src/third_party/pybind11/include/
 )

add_executable( polygames-tests
 ../src/core/game.cc
 ../src/core/state.cc
 ../src/core/model_manager.cc
 ../src/mcts/mcts.cc
 ../src/mcts/storage.cc
 ../src/mcts/node.cc
 ../src/tube/src_cpp/data_channel.cc
 ../src/core/replay_buffer.cc
 tests.cc

 # Include your tests here.
 connectfour-tests.cc
 havannah-state-tests.cc
 havannah-tests.cc
 hex-state-tests.cc
 hex-tests.cc

 # TODO: add and fix tests
 #ludii-game-tests.cc
 #../src/games/ludii/jni_utils.cc
 #../src/games/ludii/ludii_game_wrapper.cc
 #../src/games/ludii/ludii_state_wrapper.cc


 #    ../build/src/third_party/fmt/libfmt.a
  ../src/distributed/network.cc
  ../src/distributed/rdma_nop.cc
  ../src/distributed/distributed.cc
  ../src/common/thread_id.cc
  ../src/common/threads.cc
  ../src/games/weakschur/WeakSchur.cpp
  ../src/games/weakschur/SchurMatrix.cpp
  ../src/games/weakschur/SchurVector.cpp
  ../src/games/breakthrough.cc
  ../src/games/amazons.cc
../src/games/breakthrough.cc
../src/games/chess.cc
../src/games/chinesecheckers.cc
../src/games/game_base.cc
../src/games/gomoku_swap2.cc
../src/games/mastermind_state.cc
../src/games/minesweeper.cc
../src/games/nogo_action.cc
../src/games/nogo_game.cc
../src/games/nogo_state.cc
../src/games/othello_opt.cc
../src/games/tristan_nogo.cc
../src/games/yinsh.cc
 )

#link_directories(/polygames/build/src/third_party/fmt)

#file(GLOB _zstd_SOURCES ../src/third_party/zstd/lib/common/*.c ../src/third_party/zstd/lib/compress/*.c ../src/third_party/zstd/lib/decompress/*.c)
#add_library(_zstd OBJECT ${_zstd_SOURCES})

#target_include_directories(_zstd BEFORE PUBLIC ../src/third_party/zstd/lib ../src/third_party/zstd/lib/common)


#find_package(GTest CONFIG REQUIRED)
include(FetchContent)
FetchContent_Declare(
  googletest
  # Specify the commit you depend on and update it regularly.
  URL https://github.com/google/googletest/archive/5376968f6948923e2411081fd9372e71a59d8e77.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)


target_include_directories(polygames-tests PUBLIC ${PYTHON_INCLUDE_DIRS})

target_link_libraries( polygames-tests 
    ${CMAKE_THREAD_LIBS_INIT}
    ${GTEST_LIBRARIES}
    ${JNI_LIBRARIES}
    ${TORCH_LIBRARIES}
    $<TARGET_OBJECTS:_zstd>
    ${PYTHON_LIBRARIES}
    fmt
    gtest_main
    gtest
    libpolygames
    )

install (TARGETS polygames-tests DESTINATION bin)

