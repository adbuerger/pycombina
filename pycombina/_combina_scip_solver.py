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

from _combina_milp_solver import CombinaMilpSolverBaseClass

class CombinaScipSolver(CombinaMilpSolverBaseClass):

    from pyscipopt import Model, quicksum

    def setup_maximum_switching_constraints(self):

        for i in range(self.n_c):

            for j in range(self.n_b-1):

                self.model.addCons(self.s[(i,j)] >= self.b_bin_sym[(i,j)] - self.b_bin_sym[(i,j+1)])
                self.model.addCons(self.s[(i,j)] >= -self.b_bin_sym[(i,j)] + self.b_bin_sym[(i,j+1)])
                self.model.addCons(self.s[(i,j)] <= self.b_bin_sym[(i,j)] + self.b_bin_sym[(i,j+1)])
                self.model.addCons(self.s[(i,j)] <= 2 - self.b_bin_sym[(i,j)] - self.b_bin_sym[(i,j+1)])

        for i, sigma_max_i in enumerate(self.sigma_max):

            if sigma_max_i % 2 == 0:

                self.model.addCons(sigma_max_i >= self.b_bin_sym[(i,0)] - \
                    self.b_bin_sym[(i,self.n_b-1)] + self.quicksum([self.s[(i,j)] for j in range(self.n_b-1)]))
                self.model.addCons(sigma_max_i >= self.b_bin_sym[(i,self.n_b-1)] - \
                    self.b_bin_sym[(i,0)] + self.quicksum([self.s[(i,j)] for j in range(self.n_b-1)]))

            else:

                self.model.addCons(sigma_max_i >= 1 - self.b_bin_sym[(i,0)] - \
                    self.b_bin_sym[(i,self.n_b-1)] + self.quicksum([self.s[(i,j)] for j in range(self.n_b-1)]))
                self.model.addCons(sigma_max_i >= self.b_bin_sym[(i,0)] + \
                    self.b_bin_sym[(i,self.n_b-1)] - 1 + self.quicksum([self.s[(i,j)] for j in range(self.n_b-1)]))


    def setup_approximation_inequalites(self):

        for i in range(self.n_c):

            for j in range(self.n_b):

                self.model.addCons(self.eta_sym >= self.quicksum( \
                    [self.dt[k] * (self.b_rel[i][k] - self.b_bin_sym[(i,k)]) for k in range(j+1)]))
                self.model.addCons(self.eta_sym >= -self.quicksum( \
                    [self.dt[k] * (self.b_rel[i][k] - self.b_bin_sym[(i,k)]) for k in range(j+1)]))


    def solve_milp(self):

        # self.model.setRealParam("numerics/lpfeastol", 1e-17)
        self.model.optimize()


    def retrieve_solutions(self):

        self.eta = self.model.getVal(self.eta_sym)

        self.b_bin = []

        for i in range(self.n_c):

            self.b_bin.append([abs(round(self.model.getVal( \
                self.b_bin_sym[(i,j)]))) for j in range(self.n_b)])
