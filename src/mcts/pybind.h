#pragma once
#include <pybind11/pybind11.h>

namespace mcts {
    void pybind_submodule(pybind11::module& m);
}
