CMAKE_MINIMUM_REQUIRED(VERSION 3.3)
project(polygames)

set(CMAKE_CXX_STANDARD 17)

OPTION(USE_MOLD "Use mold linker if available" ON)

if(USE_MOLD)
  find_program(MOLD_FOUND mold)
  if(MOLD_FOUND)
    message(STATUS "Using mold linker: mold")
    set(LINK_FLAGS "-fuse-ld=mold")
  else()
    message(STATUS "mold linker not found, using default linker `ld`")
    set(LINK_FLAGS "-fuse-ld=lld")
  endif()
endif()


set(FLAGS_WARNINGS "-Wall -Wextra -Werror -Wno-unused-variable -Wno-unused-parameter")

set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 ${FLAGS_WARNINGS}")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-g -O3 -ffast-math ${FLAGS_WARNINGS}")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -ffast-math ${FLAGS_WARNINGS}")

set(CMAKE_C_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
set(CMAKE_C_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

OPTION(PYTORCH12 "Is PyTorch >= 1.2" OFF)
OPTION(PYTORCH15 "Is PyTorch >= 1.5" OFF)
IF(PYTORCH15)
    ADD_DEFINITIONS(-DPYTORCH15 -DPYTORCH12)
ELSEIF(PYTORCH12)
    ADD_DEFINITIONS(-DPYTORCH12)
ENDIF()

execute_process(
    COMMAND python -c "import torch; import os; print(os.path.dirname(torch.__file__), end='')"
    OUTPUT_VARIABLE TorchPath
)
set(CMAKE_PREFIX_PATH ${TorchPath})
find_package(Torch REQUIRED)

find_package(Boost COMPONENTS system)
if( Boost_FOUND )
include_directories( ${Boost_INCLUDE_DIRS})
endif()

option(WITH_LUDII "Include LUDII support" ON)

if(WITH_LUDII)
  find_package(JNI)
  if (JNI_FOUND)
      include_directories( ${JNI_INCLUDE_DIRS})
  else()
      message(STATUS "Java not found, LUDII support will not be included")
      add_definitions(-DNO_JAVA)
  endif()
else()
  add_definitions(-DNO_JAVA)
endif()

message(STATUS "Adding PyTorch compilation flags: ${TORCH_CXX_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

include_directories(src/third_party/pybind11/include/)
add_subdirectory(src)
add_subdirectory(tests)

# tests
add_executable(test_state src/core/test_state.cc src/core/state.cc)
target_link_libraries(test_state PUBLIC _tube _mcts _games ${JNI_LIBRARIES} python3.10)

enable_testing()

add_test(NAME test_replay_buffer
    COMMAND ${PYTHON_EXECUTABLE} -m test_replay_buffer
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/tests/python)

set_tests_properties(test_replay_buffer
    PROPERTIES ENVIRONMENT "PYTHONPATH=${PROJECT_SOURCE_DIR}:$ENV{PYTHONPATH}")
