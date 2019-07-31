#!/usr/bin/python
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

import signal
import numpy as np

from ._binary_approximation import BinApprox, BinApproxPreprocessed
from ._combina_bnb_solver import CombinaBnBSolver


def handle_interrupt(signum, frame):
    
    # pretty hacky, should be improved

    if signum == signal.SIGINT:
    
        a.stop()


class CombinaBnB():

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using branch-and-bound.

    The following options of :class:`pycombina.BinApprox` are supported:

    - Maximum number of switches
    - Minimum up-times
    - Minimum down-times
    - ...

    All other options are ignore without further notice.

    :param BinApprox: Binary approximation problem

    '''

    _solver_status = {

        1: "Initialized",
        2: "Optimal solution found",
        3: "Maximum number of iterations exceeded",
        4: "Maximum CPU time exceeded",
        5: "User interrupt"
    }


    @property
    def status(self):

        '''
        Exit status of the Branch-and-Bound solver.
        '''

        try:
            return self._solver_status[self._bnb_solver.get_status()]

        except KeyError:
            raise RuntimeError("Solver status undefined, this should not happen.\n"
                + "Please contact the developers.")

    @property
    def solution_time(self):

        '''
        Solution time of the Branch-and-Bound solver.
        '''

        return self._bnb_solver.get_solution_time()


    @staticmethod
    def get_search_strategies():
        return CombinaBnBSolver.search_strategies

    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_bnb(self) -> None:

        if self._binapprox_p.b_bin_pre.sum() < 1:

            b_bin_pre = self._binapprox_p.n_c + 1

        else:

            b_bin_pre = int(np.where(self._binapprox_p.b_bin_pre == 1)[0])

        self._bnb_solver = CombinaBnBSolver( \
                self._binapprox_p.dt.tolist(), \
                self._binapprox_p.b_rel.tolist(), \

                self._binapprox_p.n_c, \
                self._binapprox_p.n_t, \

                self._binapprox_p.n_max_switches.tolist(), \
                self._binapprox_p.min_up_times.tolist(), \
                self._binapprox_p.min_down_times.tolist(), \
                self._binapprox_p.max_up_times.tolist(), \
                self._binapprox_p.total_max_up_times.tolist(), \

                self._binapprox_p.b_valid.tolist(), \
                self._binapprox_p.b_adjacencies.tolist(), \

                b_bin_pre, \

            )


    def _setup_bnb(self, binapprox: BinApprox) -> None:

        self._apply_preprocessing(binapprox)
        self._initialize_bnb()


    def __init__(self, binapprox: BinApprox) -> None:

        self._setup_bnb(binapprox)


    def _setup_warm_start(self, use_warm_start: bool) -> None:

        if use_warm_start:

            raise NotImplementedError("Warm-starting not yet implemented.")


    def _run_solver(self, use_warm_start: bool, **kwargs) -> None:
        try:
            
            self._bnb_solver.run(use_warm_start, **kwargs)

        except KeyboardInterrupt:

            self._bnb_solver.stop()

        self._binapprox_p.set_b_bin(self._bnb_solver.get_b_bin())
        self._binapprox_p.set_eta(self._bnb_solver.get_eta())


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)


    def solve(self, use_warm_start: bool = False , **kwargs):

        '''
        Solve the combinatorial integral approximation problem.

        :param use_warm_start: If a binary solution is already contained in the
                               given binary approximation problem, use it to
                               warm-start the solver.

        :param strategy: Search strategy to be used in exploring the
                         branch-and-bound tree. *Default:* **dfs**. *Options:*
            - **bfs**: best first search,
            - **btd**: best then dive strategy,
            - **dfs**: depth first search,
            - **dbt**: dynamic backtracking tree search.

        :param vbc_file: Path of a VBC output file to which the branch-and-bound
                         tree should be written. **None** indicates that no VBC
                         file should be written at all. *Default:* **None**.

        :param vbc_timing: Boolean indicating whether the VBC file should contain
                           timing information. Ignored if no VBC file is written.
                           *Default:* True.

        :param vbc_time_dilation: Floating point number by which all times
                                  are multiplied prior to being written to the
                                  VBC file. Ignored if no VBC file is written.
                                  *Default:* 1.0.

        :param max_iter: Maximum number of solver iterations. Once reached, the
                         best solution found so far is returned. *Default:* 5e6.

        :param max_cpu_time: Maximum CPU seconds for the solver. Once reached,
                             the best solution found so far is returned.
                             *Default:* 3e2.

        :param verbosity: Determine how much solver information is written to
                          the console, possible values are 0 (no output),
                          1 (show results only), 2 (show iterations). 
                        *Default:* True.
        '''

        self._setup_warm_start(use_warm_start = use_warm_start)
        self._run_solver(use_warm_start = use_warm_start, **kwargs)
        self._set_solution()
