CMAKE_MINIMUM_REQUIRED(VERSION 3.3)
project(polygames)

set(CMAKE_CXX_STANDARD 17)

OPTION(USE_MOLD "Use mold linker if available" OFF)
if(USE_MOLD)
  message(STATUS "Using mold linker: mold")
  set(LINK_FLAGS "-fuse-ld=mold")
else()
  message(STATUS "mold linker not found, using default linker `ld`")
  set(LINK_FLAGS "-fuse-ld=lld")
endif()


# Compilation flags
set(FLAGS_WARNINGS "-Wall -Wextra -Werror -Wno-unused-variable -Wno-unused-value -Wno-deprecated-declarations")

# In debug use the three simultaneously supported sanitizers, see https://stackoverflow.com/a/47261999
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 ${FLAGS_WARNINGS}")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-g -O3 -ffast-math ${FLAGS_WARNINGS}")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -ffast-math ${FLAGS_WARNINGS}")

set(CMAKE_C_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
set(CMAKE_C_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Set compiler for NVCC
SET(NVCC_EXTRA_FLAGS "")  # Extra flags to prepend to NVCC
set(ENV{NVCC_PREPEND_FLAGS} "-ccbin ${CMAKE_CXX_COMPILER} ${NVCC_EXTRA_FLAGS}")

OPTION(PYTORCH12 "Is PyTorch >= 1.2" OFF)
OPTION(PYTORCH15 "Is PyTorch >= 1.5" OFF)
IF(PYTORCH15)
    ADD_DEFINITIONS(-DPYTORCH15 -DPYTORCH12)
ELSEIF(PYTORCH12)
    ADD_DEFINITIONS(-DPYTORCH12)
ENDIF()

OPTION(POLYGAMES_WITH_CUDA "Compile with CUDA support?" ON)
if(NOT POLYGAMES_WITH_CUDA)
  ADD_DEFINITIONS(-DPOLYGAMES_WITHOUT_CUDA)
endif()

# Add Pytorch from installed Pip path
execute_process(
    COMMAND python -c "import torch; import os; print(os.path.dirname(torch.__file__), end='')"
    OUTPUT_VARIABLE TorchPath
)
list(APPEND CMAKE_PREFIX_PATH ${TorchPath})
find_package(Torch REQUIRED)

# Add Pybind11 from installed Pip path
execute_process(
    COMMAND python -c "import pybind11; import os; print(os.path.dirname(pybind11.__file__), end='')"
    OUTPUT_VARIABLE Pybind11Path
)
list(APPEND CMAKE_PREFIX_PATH ${Pybind11Path})
find_package(pybind11 REQUIRED)

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

add_subdirectory(src)
add_subdirectory(tests)
