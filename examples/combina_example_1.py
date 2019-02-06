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

import argparse

import pylab as pl

import pycombina
from pycombina import BinApprox


# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--max_switches', type=int, default=4, help='maximal number of control switches allowed')
parser.add_argument('--solver', type=str, choices=['bnb', 'milp', 'sur'], default='bnb', help='specify solver for CIA problem')
if hasattr(pycombina, 'CombinaBnB'):
    bnb_group = parser.add_argument_group('Branch-and-Bound arguments')
    bnb_group.add_argument('--search_strategy', type=str, default='dfs', choices=pycombina.CombinaBnB.get_search_strategies(), help='specify tree search strategy')
    bnb_group.add_argument('--max_iter', type=int, metavar='n', default=5000000, help='maximal number of branch-and-bound iterations')
args = parser.parse_args()

pl.close("all")

data = pl.loadtxt("data/data_example_1.csv", delimiter = " ", skiprows = 1)

t = data[:,0]
b_rel = data[:-1, 1]
max_switches = [args.max_switches]

binapprox = BinApprox(t = t, b_rel = b_rel, binary_threshold = 1e-3, \
    off_state_included = False)

binapprox.set_n_max_switches(n_max_switches = max_switches)
#binapprox.set_min_up_times(min_up_times = [10])
#binapprox.set_min_down_times(min_down_times = [10])
#binapprox.set_cia_norm("column_sum_norm")

if args.solver == 'bnb':
    from pycombina import CombinaBnB
    combina = CombinaBnB(binapprox)
    combina.solve(use_warm_start=False, bnb_search_strategy=args.search_strategy, bnb_opts={'max_iter': args.max_iter})
elif args.solver == 'milp':
    from pycombina import CombinaMILP
    combina = CombinaMILP(binapprox)
    combina.solve()
else:
    from pycombina import CombinaSUR
    combina = CombinaSUR(binapprox)
    combina.solve()

b_bin = pl.squeeze(binapprox.b_bin)

pl.figure()
pl.step(t[:-1], b_rel, label = "b_rel", color = "C0", linestyle = "dashed", where = "post")
pl.step(t[:-1], b_bin, label = "b_bin", color = "C0", where = "post")
pl.xlabel("t")
pl.ylabel("b")
pl.legend(loc = "upper left")
pl.show()
