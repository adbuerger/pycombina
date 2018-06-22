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

class RoundingSolverBaseClass(object):

    __metaclass__ = ABCMeta


    def get_eta(self):

        return self.eta


    def get_b_bin(self):

        return self.b_bin


    def __init__(self, dt, b_rel, n_c, n_b):

        self.dt = dt
        self.b_rel = b_rel
        
        self.n_c = n_c
        self.n_b = n_b


    @abstractmethod
    def run_rounding_approximation(self):
        
        pass


    def run(self):

        self.run_rounding_approximation()
