/*
 *
 * PythonBindings.cpp
 *
 * This file is part of pycombina.
 *
 * Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
 *
 * pycombina is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pycombina is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with pycombina. If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <vector>

#ifndef PYBIND11
#define PYBIND11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#endif
 
#include "CombinaBnBSolver.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_combina_bnb_solver, m)
{
    py::class_<CombinaBnBSolver>(m, "CombinaBnBSolver")
        .def(py::init<std::vector<double> const &,
                      std::vector<std::vector<double>> const &,

                      unsigned int const &,
                      unsigned int const &,

                      std::vector<unsigned int> const &,
                      std::vector<double> const &,
                      std::vector<double> const &,
                      std::vector<std::vector<unsigned int>> &,
                      std::vector<std::vector<unsigned int>> &,

                      unsigned int const &>())

        .def("get_eta", &CombinaBnBSolver::get_eta)
        .def("get_b_bin", &CombinaBnBSolver::get_b_bin)

        .def("run", &CombinaBnBSolver::run, py::arg("use_warm_start"),
                                      py::arg("bnb_opts"))
        .def("stop", &CombinaBnBSolver::stop);
}
