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

from _rounding_solver import RoundingSolverBaseClass

class RoundingSurSolver(RoundingSolverBaseClass):

    def run_rounding_approximation(self):

        self.b_bin = []
    
        mysum = 0.0

        for i in range(self.n_b):
            
            mysum = mysum + self.b_rel[0][i] * self.dt[i] 

            if (mysum < 0.5 * self.dt[i]):
            
                self.b_bin.append(0) 
            
            else:
            
                self.b_bin.append(1)
                mysum = mysum - 1.0 * self.dt[i]
            
            self.eta = mysum

    def retrieve_solutions(self):
        
        self.b_bin = self.b_bin
        self.eta = self.eta

