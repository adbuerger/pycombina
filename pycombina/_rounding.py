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

class Rounding(BinaryApproximationBaseClass):

    def _check_available_solvers(self):

        self._available_solvers = {}

        try:
            from _rounding_sur_solver import RoundingSurSolver
            self._available_solvers["sur"] = RoundingSurSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- pycombina Sum-Up-Rounding extension not found, SUR solver disabled.")

        if not self._available_solvers:
            raise RuntimeError("No solvers available for pycombina.")


    def _solve_binary_approximation_problem(self, solver):

        try:
            self._solver = self._available_solvers[solver]( \
                self._dt, self._b_rel, self._n_c, self._n_b)

        except KeyError:
            raise ValueError("Unknown solver '" + solver + "', valid options are:\n" + \
                str(self._available_solvers.keys()))

        self._solver.run()


    def solve(self, solver = 'sur'):

        r'''
        :raises: ValueError, NotImplementedError

        :param solver: Specifies which solver to use to solve the rounding
                       binary approximation problem. Possible options are:

                       * 'sur' - solve using standard, decoupled Sum-Up-Rounding

                       Availability of solvers depends on whether the necessary
                       libraries and Python interfaces are installed on your
                       system. Also, not all solver options are available
                       for all solvers.
        :type solver: str

        Solve the rounding binary approximation problem considering
        the specified options.

        '''

        self._compute_time_grid_from_time_points()
        self._numpy_arrays_to_lists()

        self._check_init_active_control()
        self._solve_binary_approximation_problem(solver)
        self._retrieve_solution()
        self._lists_to_numpy_arrays()
        self._determine_number_of_control_intervals()
