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

import time
from typing import Any, Dict, List, Optional

import numpy as np
import pulp

from ._binary_approximation import BinApprox, BinApproxPreprocessed


class CombinaMILP():

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using mixed-integer linear programming and Gurobi.

    The following options of :class:`pycombina.BinApprox` are supported:

    - Maximum number of switches
    - Minimum up-times
    - Minimum down-times
    - Valid control transitions (b_adjacencies)
    - Valid controls per interval (b_valid)
    - Active control at time point t_0-1 (b_bin_pre)

    All other options are ignored without further notice.

    :param BinApprox: Binary approximation problem

    '''

    _solver_status = {

        1: "Initialized",
        2: "Optimal solution found",
        7: "Maximum number of iterations exceeded",
        9: "Maximum CPU time exceeded",
        11: "User interrupt"
    }

    def __init__(self, binapprox: BinApprox) -> None:

        self._model = pulp.LpProblem("CIA-MILP", pulp.LpMinimize)
        self._apply_preprocessing(binapprox)
        self._setup_milp(binapprox)


    @property
    def status(self):

        try:
            return self._solver_status[self._model.status]

        except KeyError:
            raise RuntimeError("Solver status undefined, this should not happen.\n"
                + "Please contact the developers.")

    @staticmethod
    def _ij_names(imax: int, jmax: int, jmin: int = 0) -> List[str]:
        return [(i,j) for i in range(imax) for j in range(jmin, jmax)]

    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_milp(self):

        self._model = pulp.LpProblem("CIA-MILP")


    def _setup_model_variables(self):

        print("\n  - Optimization variables ... ", end = "", flush = True)

        self._eta_sym = pulp.LpVariable(name="eta")

        if (self._binapprox_p.cia_norm == "column_sum_norm") or (self._binapprox_p.cia_norm == "row_sum_norm"):

            self._eta_sym_indiv = pulp.LpVariable.dicts(
                "eta_sym_indiv_",
                self._ij_names(self._binapprox_p.n_c, self._binapprox_p.n_t),
            )

        self._b_bin_sym = {}
        self._s = {}

        self._s = pulp.LpVariable.dicts(
            "s_",
            self._ij_names(self._binapprox_p.n_c, self._binapprox_p.n_t-1, jmin=-1)
        )
        self._b_bin_sym = pulp.LpVariable.dicts(
            "b_bin",
            self._ij_names(self._binapprox_p.n_c, self._binapprox_p.n_t, jmin=-1),
            cat=pulp.constants.LpBinary
        )

        print("done")


    def _setup_b_bin_pre_variables(self):

        for i in range(self._binapprox_p.n_c):

            if self._binapprox_p.b_bin_pre.sum() == 1:

                self._model += (self._b_bin_sym[(i,-1)] == int(self._binapprox_p.b_bin_pre[i]))


    def _setup_objective(self):

        print("  - Objective ... ", end = "", flush = True)

        self._model += self._eta_sym

        print("done")


    def _setup_approximation_inequalities(self):

        print("  - Approximation inequalities ... ", end = "", flush = True)

        if self._binapprox_p.cia_norm == "max_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = 0.0
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs += self._binapprox_p.dt[j] * self._b_bin_sym[(i,j)]
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model += (lhs + self._eta_sym >= rhs)
                    self._model += (lhs - self._eta_sym <= rhs)

                    # self._model.addConstr(self._eta_sym >= sum( \
                    #     [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))
                    # self._model.addConstr(self._eta_sym >= -sum( \
                    #     [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))

        elif self._binapprox_p.cia_norm == "column_sum_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = 0.0
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs += self._binapprox_p.dt[j] * self._b_bin_sym[(i,j)]
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model += (lhs + self._eta_sym_indiv[(i,j)] >= rhs)
                    self._model += (lhs - self._eta_sym_indiv[(i,j)] <= rhs)

            for j in range(self._binapprox_p.n_t):

                self._model += (
                    self._eta_sym >= pulp.lpSum([self._eta_sym_indiv[(i,j)] for i in range(self._binapprox_p.n_c)])
                )

        elif self._binapprox_p.cia_norm == "row_sum_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = 0.0
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs += self._binapprox_p.dt[j] * self._b_bin_sym[(i,j)]
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model += (lhs + self._eta_sym_indiv[(i,j)] >= rhs)
                    self._model += (lhs - self._eta_sym_indiv[(i,j)] <= rhs)

            for i in range(self._binapprox_p.n_c):

                self._model += (
                    self._eta_sym >= pulp.lpSum([self._eta_sym_indiv[(i,j)] for j in range(self._binapprox_p.n_t)])
                )

        print("done")


    def _setup_sos1_constraints(self):

        print("  - SOS1 constraints ... ", end = "", flush = True)

        for j in range(self._binapprox_p.n_t):

            self._model += (
                pulp.lpSum([self._b_bin_sym[(i,j)] for i in range(self._binapprox_p.n_c)]) == 1
            )

        print("done")


    def _setup_maximum_switching_constraints(self):

        print("  - Maximum switching constraints ... ", end = "", flush = True)

        for i in range(self._binapprox_p.n_c):

            for j in range(-1,self._binapprox_p.n_t-1):

                self._model += (self._s[(i,j)] >= self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])
                self._model += (self._s[(i,j)] >= -self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model += (self._s[(i,j)] <= self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model += (self._s[(i,j)] <= 2 - self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])

        for i, sigma_max_i in enumerate(self._binapprox_p.n_max_switches):

            if sigma_max_i % 2 == 0:

                self._model += ((self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + pulp.lpSum([self._s[(i,j)] for j in range(-1,self._binapprox_p.n_t-1)])) <= sigma_max_i)
                self._model += ((self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - self._b_bin_sym[(i,-1)] + pulp.lpSum([self._s[(i,j)] for j in range(-1,self._binapprox_p.n_t-1)])) <= sigma_max_i)

            else:

                self._model += ((1 - self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + pulp.lpSum([self._s[(i,j)] for j in range(-1, self._binapprox_p.n_t-1)])) <= sigma_max_i)
                self._model += ((self._b_bin_sym[(i,-1)] + self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - 1 + pulp.lpSum([self._s[(i,j)] for j in range(-1, self._binapprox_p.n_t-1)])) <= sigma_max_i)

        print("done")


    def _setup_dwell_time_constraints(self):

        print("  - Dwell time constraints ... ", end = "", flush = True)

        dt_sums = np.zeros((self._binapprox_p.n_t, self._binapprox_p.n_t))

        for j in range(self._binapprox_p.n_t):

                dt_sums[j][j] = self._binapprox_p.dt[j]

                for k in range(j+1,self._binapprox_p.n_t):

                    dt_sums[j][k] =  dt_sums[j][k-1] + self._binapprox_p.dt[k]

        for i in range(self._binapprox_p.n_c):

            for k in range(1,self._binapprox_p.n_t):

                if dt_sums[0][k-1] < self._binapprox_p.min_up_times[i]:
                    self._model += (self._b_bin_sym[(i,k)] - self._b_bin_sym[(i,0)] >= 0.0)

            for j in range(1,self._binapprox_p.n_t):

                for k in range(j+1,self._binapprox_p.n_t):

                    if dt_sums[j][k-1] < self._binapprox_p.min_up_times[i]:
                        self._model += (self._b_bin_sym[(i,k)] - self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j-1)] >= 0.0)

                    if dt_sums[j][k-1] < self._binapprox_p.min_down_times[i]:
                        self._model += (self._b_bin_sym[(i,k)] + self._b_bin_sym[(i,j-1)] - self._b_bin_sym[(i,j)] <= 1.0)

        print("done")


    def _setup_valid_control_transitions_constraints(self):

        print("  - Valid control transitions constraints ... ", end = "", flush = True)

        for i in range(self._binapprox_p.n_c):

            for j in range(1,self._binapprox_p.n_t):

                self._model += (1 >= self._b_bin_sym[(i,j)] +
                    pulp.lpSum([self._b_bin_sym[(l,j-1)] for l in range(self._binapprox_p.n_c) if self._binapprox_p.b_adjacencies[l][i] == 0]))

        print("done")


    def _setup_valid_controls_for_intervals_constraints(self):

        print("  - Valid controls for intervals constraints ... ", end = "", flush = True)

        for i in range(self._binapprox_p.n_c):

            for j in range(self._binapprox_p.n_t):

                if self._binapprox_p.b_valid[i][j] == 0:

                    self._model += (self._b_bin_sym[(i,j)] == 0)

        print("done")



    def _setup_milp(self, binapprox: BinApprox) -> None:

        print("Setting up MILP model for Gurobi:")

        start_time = time.time()

        self._setup_model_variables()
        self._setup_b_bin_pre_variables()
        self._setup_objective()
        self._setup_approximation_inequalities()
        self._setup_sos1_constraints()
        self._setup_maximum_switching_constraints()
        self._setup_dwell_time_constraints()
        self._setup_valid_control_transitions_constraints()
        self._setup_valid_controls_for_intervals_constraints()


        print("\nModel set up finished after", \
            round(time.time() - start_time, 2), "seconds\n")


    def __init__(self, binapprox: BinApprox) -> None:

        self._apply_preprocessing(binapprox)
        self._initialize_milp()
        self._setup_milp(binapprox)



    def _setup_warm_start(self, use_warm_start: bool) -> None:

        if use_warm_start:

            raise NotImplementedError("Warm-starting not yet implemented.")

            # for i in range(self._binapprox_p.n_c):

            #     for j in range(self._binapprox_p.n_t):

            #         self._b_bin_sym[(i,j)].start = self._binapprox_p._b_bin[i][j]


    def _run_solver(self, solver: str, opts: Dict[str, Any]) -> None:

        solver = pulp.getSolver(solver)
        self._model.solve(solver)


    def _retrieve_solutions(self):

        self._binapprox_p._eta = self._eta_sym.varValue
        self._binapprox_p._b_bin = []

        for i in range(self._binapprox_p.n_c):

            self._binapprox_p._b_bin.append([np.abs(np.round(
                self._b_bin_sym[(i,j)].varValue)) for j in range(self._binapprox_p.n_t)])


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)


    def solve(
        self,
        solver: str = "PULP_CBC_CMD",
        use_warm_start: bool = False,
        opts: Optional[Dict[str, Any]] = None
    ) -> None:
        '''
        Solve the combinatorial integral approximation problem.

        :param use_warm_start: If a binary solution is already contained in the
                               given binary approximation problem, use it to
                               warm-start the solver.
        :param opts: Solver options. Examples for Gurobi are:

            - **MIPGap**: relative MIP optimality gap; when solution found fulfilling
              the gap, Gurobi stops. Default: 0.0001
            - **TimeLimit**: Limits the total time expended (in seconds). Default: Infinity

        '''

        if opts is None:
            opts = {}

        self._setup_warm_start(use_warm_start = use_warm_start)
        self._run_solver(solver=solver, opts = opts)
        self._retrieve_solutions()
        self._set_solution()

        print("\n")
