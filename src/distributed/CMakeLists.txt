cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

find_path(IBV_INCLUDE_DIR infiniband/verbs.h)
find_library(IBV_LIBRARY ibverbs)

add_library(_distributed STATIC
  network.cc
  distributed.cc
)
target_include_directories(_distributed SYSTEM PUBLIC ${TORCH_INCLUDE_DIRS})
target_include_directories(_distributed PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)

if (IBV_INCLUDE_DIR AND IBV_LIBRARY)
  message(STATUS "Found ibverbs: ${IBV_INCLUDE_DIR}/infiniband/verbs.h ${IBV_LIBRARY}")
  target_sources(_distributed PRIVATE ib.cc)
  target_include_directories(_distributed SYSTEM PUBLIC ${IBV_INCLUDE_DIR})
  target_link_libraries(_distributed PUBLIC ${IBV_LIBRARY})
else()
  message(STATUS "ibverbs NOT found, InfiniBand support will be disabled!")
  target_sources(_distributed PRIVATE rdma_nop.cc)
endif()
