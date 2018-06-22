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

from abc import ABCMeta, abstractmethod, abstractproperty

class CombinaMilpSolverBaseClass(object):

    __metaclass__ = ABCMeta


    def get_eta(self):

        return self.eta

    def get_b_bin(self):

        return self.b_bin


    def __init__(self, dt, b_rel, n_c, n_b, *args):

        self.dt = dt
        self.b_rel = b_rel
        
        self.n_c = n_c
        self.n_b = n_b


    def setup_sigma_max(self, max_switches):

        self.sigma_max = max_switches


    def setup_dwell_time(self, min_up_time):

        self.dwell_time = min_up_time

        if not all(m == 0 for m in min_up_time):

            raise NotImplementedError("Use of dwell times with MILP solvers not yet implemented.")


    def initialize_model(self):

        self.model = self.Model("Combinatorial Integral Approximation MILP")


    def setup_model_variables(self):

        self.eta_sym = self.model.addVar(vtype = "C", name = "eta")

        self.b_bin_sym = {}
        self.s = {}

        for i in range(self.n_c):
        
            for j in range(self.n_b-1):

                self.s[(i,j)] = self.model.addVar(vtype = "C", \
                    name = "s_{0}".format((i,j)))

                self.b_bin_sym[(i,j)] = self.model.addVar( \
                    vtype = "B", name = "b_bin_{0}".format((i,j)))

            self.b_bin_sym[(i, self.n_b-1)] = self.model.addVar( \
                vtype = "B", name = "b_bin_{0}".format((i,self.n_b-1)))

        
    def setup_objective(self):

        self.model.setObjective(self.eta_sym)


    @abstractmethod
    def setup_maximum_switching_constraints(self):

        r'''
        We set up only the relevant facets, see:
        Sager et al.: Combinatorial integral approximation, 2011
        '''


    @abstractmethod
    def setup_approximation_inequalites(self):
        
        pass


    def setup_milp(self):

        self.initialize_model()
        self.setup_model_variables()

        # Here try/except still to add for Gurobi version 6.5
        #self.model.update()
        
        self.setup_objective()
        self.setup_maximum_switching_constraints()
        self.setup_approximation_inequalites()
        self.setup_sos1_constraints()


    @abstractmethod
    def solve_milp(self):
        
        pass


    @abstractmethod
    def retrieve_solutions(self):
        
        pass


    def run(self, max_switches, min_up_time):

        self.setup_sigma_max(max_switches)
        self.setup_dwell_time(min_up_time)
        self.setup_milp()
        self.solve_milp()
        self.retrieve_solutions()
