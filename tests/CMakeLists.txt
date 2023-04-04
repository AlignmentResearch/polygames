include_directories(
../src
 ../src/games
 ../src/third_party
 ../src/third_party/fmt/include
 ../src/tube/src_cpp
 ../src/third_party/pybind11/include/
 )

include(FetchContent)
FetchContent_Declare(
  googletest
  # Specify the commit you depend on and update it regularly.
  URL https://github.com/google/googletest/archive/5376968f6948923e2411081fd9372e71a59d8e77.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()
add_executable( polygames-tests
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
 )

target_include_directories(polygames-tests PRIVATE SYSTEM ${TORCH_INCLUDE_DIRS})
target_link_libraries(polygames-tests
    libpolygames
    ${GTEST_LIBRARIES}
    gtest
    GTest::gtest_main
)
include(GoogleTest)
gtest_discover_tests(polygames-tests)
