# -*- coding: utf-8 -*-
#
# This file is part of pycombina.
#
# Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
#
# pycombina is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycombina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pycombina. If not, see <http://www.gnu.org/licenses/>.

import os
import time
import numpy as np

from _binary_approximation import BinaryApproximationBaseClass

class Combina(BinaryApproximationBaseClass):

    @property
    def max_switches(self):

        '''Maximum possible amount of switches per control.'''

        try:
            return self._max_switches

        except AttributeError:
           raise AttributeError("max_switches not yet available, call solve() first.")


    @property
    def min_up_time(self):

        '''Minimum up time per control.'''

        try:
            return self._min_up_time

        except AttributeError:
           raise AttributeError("min_up_time not yet available, call solve() first.")


    def _check_available_solvers(self):

        self._available_solvers = {}

        try:
            from _combina_bnb_solver import CombinaBnBSolver
            self._available_solvers["bnb"] = CombinaBnBSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- pycombina C++ extension not built, BnB solver disabled.")

        try:
            import pyscipopt
            from _combina_scip_solver import CombinaScipSolver
            self._available_solvers["scip"] = CombinaScipSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- pyscipopt not found, SCIP solver disabled.")

        try:
            import gurobipy
            from _combina_gurobi_solver import CombinaGurobiSolver
            self._available_solvers["gurobi"] = CombinaGurobiSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- gurobipy not found, Gurobi solver disabled.")

        if not self._available_solvers:
            raise RuntimeError("No solvers available for pycombina.")


    def _validate_max_switches_input(self, max_switches):

        try:
            if not np.atleast_1d(np.squeeze(max_switches)).ndim == 1:
                raise ValueError

            if hasattr(self, "_active_controls"):
                max_switches = list(np.asarray(max_switches)[self._active_controls])
            else:
                max_switches = list(np.asarray(max_switches))
            self._max_switches = [int(s) for s in max_switches]

            if not len(self._max_switches) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("The number of integer values in max_switches must be equal to the number of binary controls.")


    def _validate_min_up_time_input(self, min_up_time):

        if min_up_time is None:

           min_up_time = [0.0] * self._n_c

        try:

            if not np.atleast_1d(np.squeeze(min_up_time)).ndim == 1:
                raise ValueError

            if hasattr(self, "_active_controls"):
                min_up_time = list(np.asarray(min_up_time)[self._active_controls])
            else:
                min_up_time = list(np.asarray(min_up_time))
            self._min_up_time = [float(m) for m in min_up_time]

            if not len(self._min_up_time) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_up_time must be equal to the number of binary controls.")


    def _validate_w_b_input(self, w_b):

        if w_b is None:

           w_b = [1.0] * self._n_c

        try:

            if not np.atleast_1d(np.squeeze(w_b)).ndim == 1:
                raise ValueError

            w_b = list(np.asarray(w_b))
            
            self._w_b = [float(w) for w in w_b]

            if not len(self._w_b) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in w_b must be equal to the number of binary controls.")


    def _solve_binary_approximation_problem(self, solver):

        if not np.all(np.isin(self._min_up_time, [0])) and solver in ["scip, gurobi"]:

            raise NotImplementedError("Min up times are not supported for solver " + solver + ".")


        if not np.all(np.isin(self._w_b, [1.0])) and solver in ["scip, gurobi"]:

            raise NotImplementedError("Use of different weightings for binary controls is not supported for solver " + solver + ".")


        if hasattr(self, "_dt_lock") and solver in ["scip, gurobi"]:

            raise NotImplementedError("Locking of initial binary sequences is only supported for solver " + solver + ".")

        try:
            self._solver = self._available_solvers[solver]( \
                self._dt, self._b_rel, self._n_c, self._n_b, self._w_b, self._init_active_control)

        except KeyError:
            raise ValueError("Unknown solver '" + solver + "', valid options are:\n" + \
                str(self._available_solvers.keys()))

        self._solver.run(max_switches = self._max_switches, min_up_time = self._min_up_time)


    def solve(self, solver = 'bnb', max_switches = [2], min_up_time = None, w_b = None):

        r'''
        :raises: ValueError, NotImplementedError

        :param solver: Specifies which solver to use to solve the combinatorial
                       integral approximation problem. Possible options are:

                       * 'bnb' - solve using a custom Branch-and-Bound algorithm
                       * 'scip' - solve using a MILP formulation with SCIP
                       * 'gurobi' - solve using a MILP formulation with Gurobi

                       Availability of solvers depends on whether the necessary
                       libraries and Python interfaces are installed on your
                       system. Also, not all solver options are available
                       for all solvers.
        :type solver: str

        :param max_switches: Array of integer values that specifies the maximum
                             number of allowed switching actions per control.
        :type max_switches: list, numpy.ndarray

        :param min_up_time: Specifies the minimum time per control that must
                            pass in between two switching actions. If None,
                            no minimum time is considered.
        :type min_up_time: None, list, numpy.ndarray

        :param w_b: Weighting of the controls for the integral approximation
                    problem.
        :type w_b: None, list, numpy.ndarray

        Solve the combinatorial integral approximation problem considering
        the specified options.

        '''

        self._compute_time_grid_from_time_points()
        self._numpy_arrays_to_lists()
        self._validate_max_switches_input(max_switches)
        self._validate_min_up_time_input(min_up_time)
        self._validate_w_b_input(w_b)

        self._check_init_active_control()
        self._solve_binary_approximation_problem(solver)
        self._retrieve_solution()
        self._lists_to_numpy_arrays()
        self._determine_number_of_control_intervals()
