/*
 *
 * pycombina.cpp
 *
 */

#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "CIA.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_cia, m)
{
    py::class_<CIA>(m, "CIA")
        .def(py::init<const std::vector<double> &, const std::vector<double> &>())

        .def("get_T", &CIA::get_T)
        .def("get_b_rel", &CIA::get_b_rel)

        .def("get_eta", &CIA::get_eta)
        .def("get_Tg", &CIA::get_Tg)

        .def("get_b_bin", &CIA::get_b_bin)

        .def("run_cia", &CIA::run_cia, py::arg("sigma_max") = 2);
}
