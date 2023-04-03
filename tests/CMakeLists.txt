include_directories(
../src
 ../src/games
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

 # Include your tests here.
 connectfour-tests.cc
 havannah-state-tests.cc
 havannah-tests.cc
 hex-state-tests.cc
 hex-tests.cc
 test_state.cc
 test_mcts.cc

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

  GTest::gtest_main
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
    gtest
    libpolygames
    _tube
    _mcts
    _games
    )

install (TARGETS polygames-tests DESTINATION bin)

