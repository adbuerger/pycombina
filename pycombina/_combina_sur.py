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

import numpy as np
import time

from ._binary_approximation import BinApprox, BinApproxPreprocessed

class CombinaSUR():

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using Sum-Up-Rounding, i.e., an approximation of the global solution.

    CombinaSUR does not support further options of :class:`pycombina.BinApprox`.
    These are ignored without further notice.

    :param BinApprox: Binary approximation problem

    '''

    _solver_status = {

        1: "Initialized",
        2: "Optimal solution found",
    }


    @property
    def status(self):

        try:
            return self._solver_status[self._sur_status]

        except KeyError:
            raise RuntimeError("Solver status undefined, this should not happen.\n"
                + "Please contact the developers.")


    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _set_sur_status(self, sur_status):

        self._sur_status = sur_status


    def _welcome_prompt_sur(self):

        print("-----------------------------------------------------------")
        print("                                                           ")
        print("                 pycombina Sum-Up-Rounding                 ")
        print("                                                           ")


    def _setup_sur(self, binapprox: BinApprox) -> None:

        self._welcome_prompt_sur()
        self._apply_preprocessing(binapprox)
        self._set_sur_status(sur_status = 1)


    def __init__(self, binapprox: BinApprox) -> None:

        self._setup_sur(binapprox)

 
    def solve(self, *args, **kwargs):

        '''
        Solve the combinatorial integral approximation problem.

        '''

        self._run_sur()
        self._set_solution()
        self._set_sur_status(sur_status = 2)

        print("\n-----------------------------------------------------------")


    def _run_sur(self):

        print("Running Sum-up-rounding ... ", end = "", flush = True)

        start_time = time.time()

        b_bin = np.zeros((self._binapprox_p.n_c, self._binapprox_p.n_t))
        eta_i = np.zeros(self._binapprox_p.n_c)
        eta = 0.0

        for i in range(self._binapprox_p.n_t):

            b_active = 0

            for j in range(self._binapprox_p.n_c):

                eta_i[j] = eta_i[j] + self._binapprox_p.b_rel[j][i] * self._binapprox_p.dt[i] 

                if (eta_i[j] > eta_i[b_active]):

                    b_active = j

            b_bin[b_active][i] = 1

            eta_i[b_active] =  eta_i[b_active] - 1 * self._binapprox_p.dt[i] 
            eta = max(eta, np.abs(eta_i).max())
        
        self._binapprox_p._b_bin = b_bin
        self._binapprox_p._eta = eta

        print("done")

        print("\n    Best solution: {:.6e}".format(eta))
        print("    Total runtime: {:.6e} s".format(time.time() - start_time))


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)
