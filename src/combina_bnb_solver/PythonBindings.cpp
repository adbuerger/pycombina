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

#include "CombinaBnBSolver.hpp"
#include "NodeQueue.hpp"
#include "monitors/VbcMonitor.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <map>
#include <vector>


namespace py = pybind11;


// function prototypes
static void combina_wrap_run(CombinaBnBSolver& solver, bool use_warm_start, py::kwargs kwargs);


// Table of node queue configurators
static const std::map<std::string, std::function<void (NodeQueuePtr, const py::dict&)>> queue_configurators {
};


PYBIND11_MODULE(_combina_bnb_solver, m)
{
    // register default search strategies
    NodeQueue::register_default_types();

    // set up combina solver interface
    py::class_<CombinaBnBSolver>(m, "CombinaBnBSolver")
        .def(py::init<std::vector<double> const &,
                      std::vector<std::vector<double>> const &,

                      unsigned int const &,
                      unsigned int const &,

                      std::vector<unsigned int> const &,
                      std::vector<double> const &,
                      std::vector<double> const &,
                      std::vector<double> const &,
                      std::vector<double> const &,

                      std::vector<std::vector<unsigned int>> &,
                      std::vector<std::vector<unsigned int>> &,

                      unsigned int const &>())

        .def("get_eta", &CombinaBnBSolver::get_eta)
        .def("get_b_bin", &CombinaBnBSolver::get_b_bin)
        .def("get_status", &CombinaBnBSolver::get_status)
        .def("get_solution_time", &CombinaBnBSolver::get_solution_time)

        .def_property_readonly_static("search_strategies", [](py::object) { return NodeQueue::get_types(); })

        .def("run", &combina_wrap_run, py::arg("use_warm_start"))
        .def("stop", &CombinaBnBSolver::stop);
}


static void combina_wrap_run(CombinaBnBSolver& solver, bool use_warm_start, py::kwargs kwargs) {
    // create specialized node queue
    if(kwargs.contains("strategy")) {
        const std::string type = py::str(kwargs["strategy"]);

        // create node queue using factory (throws std::out_of_range for
        // non-existent types)
        NodeQueuePtr node_queue = NodeQueue::create(&solver, type);

        // configure node queue using remaining arguments
        auto config = queue_configurators.find(type);
        if(config != queue_configurators.end()) {
            config->second(node_queue, kwargs);
        }

        // install node queue in solver
        solver.set_node_queue(node_queue);
    }

    // configure monitor if requested
    if(kwargs.contains("vbc_file")) {
        const py::object arg = kwargs["vbc_file"];

        if(arg.is_none() || !py::bool_(arg)) {
            // remove current monitor if present
            solver.set_monitor(nullptr);
        }
        else {
            // find the timing flag
            bool timing = true;
            if(kwargs.contains("vbc_timing")) {
                timing = py::bool_(kwargs["vbc_timing"]);
            }

            // create new VbcMonitor
            const std::string path = py::str(arg);
            auto vbc_mon = std::make_shared<VbcMonitor>(&solver, path, timing);

            // configure time dilation
            if(kwargs.contains("vbc_time_dilation")) {
                vbc_mon->set_time_dilation(py::float_(kwargs["vbc_time_dilation"]));
            }

            // install monitor
            solver.set_monitor(vbc_mon);
        }
    }

    // set additional parameters
    if(kwargs.contains("max_iter")) {
        solver.set_max_iter(py::cast<long>(kwargs["max_iter"]));
    }
    if(kwargs.contains("max_cpu_time")) {
        solver.set_max_cpu_time(py::cast<double>(kwargs["max_cpu_time"]));
    }

    if(kwargs.contains("verbosity")) {
        solver.set_verbosity(py::cast<int>(kwargs["verbosity"]));
    }

    // invoke run function
    {
        py::gil_scoped_release release;
        solver.run(use_warm_start);
    }
}
