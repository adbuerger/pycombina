// pycombina.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "cia.hpp"

namespace py = pybind11;

PYBIND11_PLUGIN(pycombina)
{
    py::module m("pycombina");
    m.def("cia", &cia);
    return m.ptr();
}
