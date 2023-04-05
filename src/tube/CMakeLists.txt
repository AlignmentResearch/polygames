cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

add_library(_tube STATIC
  src_cpp/data_channel.cc
  src_cpp/pybind.cc
)
target_include_directories(_tube SYSTEM PUBLIC ${TORCH_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS} ${ZEROMQ_INCLUDE_DIRS})
target_link_directories(_tube PUBLIC ${TORCH_INSTALL_PREFIX}/lib)
target_link_libraries(_tube PUBLIC ${TORCH_LIBRARIES} fmt ${ZEROMQ_LIBRARIES} torch_python)


# We don't add the pybind11 module on purpose -- let `libpolygames` link all of it.
# pybind11_add_module(tube src_cpp/pybind.cc)
