/*
 *
 * pycombina.cpp
 *
 */

#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "CombinaBnBSolver.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_combina_bnb_solver, m)
{
    py::class_<CombinaBnBSolver>(m, "CombinaBnBSolver")
        .def(py::init<const std::vector<double> &, const std::vector<std::vector<double>> &, 
            const unsigned int&, const unsigned int&>())

        .def("get_eta", &CombinaBnBSolver::get_eta)
        .def("get_b_bin", &CombinaBnBSolver::get_b_bin)

        .def("run", &CombinaBnBSolver::run, py::arg("sigma_max"));
}
