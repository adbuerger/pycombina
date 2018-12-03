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
    
    # very dirty hack, should be improved

    if signum == signal.SIGINT:
    
        a.stop()


class CombinaBnB():

    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_bnb(self) -> None:

        if self._binapprox_p.b_bin_pre.sum() < 1:

            b_bin_pre = self._binapprox_p.n_c + 1

        else:

            b_bin_pre = int(np.where(self._binapprox_p.b_bin_pre == 1))

        self._bnb_solver = CombinaBnBSolver( \
                self._binapprox_p.dt.tolist(), \
                self._binapprox_p.b_rel.tolist(), \

                self._binapprox_p.n_c, \
                self._binapprox_p.n_t, \

                self._binapprox_p.n_max_switches.tolist(), \
                self._binapprox_p.min_up_times.tolist(), \
                self._binapprox_p.min_down_times.tolist(), \
                self._binapprox_p.b_valid.tolist(), \
                self._binapprox_p.b_adjacencies.tolist(), \

                self._binapprox_p.min_down_times_pre.tolist(), \
                b_bin_pre, \

            )


    def _setup_bnb(self, binapprox: BinApprox) -> None:

        self._apply_preprocessing(binapprox)
        self._initialize_bnb()


    def __init__(self, binapprox: BinApprox) -> None:

        self._setup_bnb(binapprox)


    def _run_solver(self, use_warm_start: bool, bnb_opts: dict) -> None:

        bnb_opts_default = {

            "max_iter" :  5e6,
            "max_cpu_time": 3e2,
        }

        for bnb_opt in bnb_opts.keys():

            try:

                bnb_opts_default.update({bnb_opt: float(bnb_opts[bnb_opt])})

            except ValueError:

                raise ValueError("Values of solver options must be of numerical type.")

        try:
            
            self._bnb_solver.run(use_warm_start, bnb_opts_default)

        except KeyboardInterrupt:

            self._bnb_solver.stop()

        self._binapprox_p.set_b_bin(self._bnb_solver.get_b_bin())
        self._binapprox_p.set_eta(self._bnb_solver.get_eta())


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)


    def solve(self, use_warm_start: bool = False , bnb_opts: dict = {}):

        self._run_solver(use_warm_start = use_warm_start, bnb_opts = bnb_opts)
        self._set_solution()
