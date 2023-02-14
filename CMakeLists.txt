CMAKE_MINIMUM_REQUIRED(VERSION 3.3)
project(polygames)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} -fsized-deallocation -O3 -ffast-math")

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

add_subdirectory(src)

