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

import argparse as ap
import sys

import numpy as np
import pylab as pl

from pycombina import BinApprox

# parse command line arguments
parser = ap.ArgumentParser()
parser.add_argument('--solver', type=str, choices=['milp', 'bnb', 'sur'], default='bnb', help='specify CIA solver')
parser.add_argument('--max_switches', metavar=['n_a', 'n_b', 'n_c'], type=int, nargs=3, default=[5, 2, 3], help='specify maximum number of switches')
bnb_group = parser.add_argument_group('Branch-and-bound solver')
bnb_group.add_argument('--max_iter', metavar='n', type=int, default=5000000, help='specify iteration limit')
bnb_group.add_argument('--search_strategy', type=str, choices=['bfs', 'dfs', 'dbt'], default='dfs', help='specify tree search strategy')
args = parser.parse_args()

pl.close("all")

data = pl.loadtxt("data/mmlotka_nt_12000_400.csv", delimiter = " ", skiprows = 1)

dN = 8	

t = data[::dN,0]
b_rel = data[:-1:dN, 3:]

max_switches = args.max_switches

binapprox = BinApprox(t = t, b_rel = b_rel, binary_threshold = 1e-3, \
        off_state_included = True)
binapprox.set_n_max_switches(n_max_switches = max_switches)

#binapprox.set_valid_controls_for_interval((0, 2), [1,0,0])
#binapprox.set_valid_control_transitions(0, [1,0,1])
#binapprox.set_min_up_times([2.0, 2.0, 2.0])
#binapprox.set_cia_norm("row_sum_norm")
	
#binapprox.set_b_bin_pre([1,0,0])

if args.solver == 'milp':
    from pycombina import CombinaMILP
    combina = CombinaMILP(binapprox)
    combina.solve()
elif args.solver == 'bnb':
    from pycombina import CombinaBnB
    combina = CombinaBnB(binapprox)
    combina.solve(use_warm_start=False, bnb_search_strategy=args.search_strategy, bnb_opts={
        'max_iter': args.max_iter
    }) #, gurobi_opts = {"TimeLimit": 20, "MIPGap": 0.4})
elif args.solver == 'sur':
    from pycombina import CombinaSUR
    combina = CombinaSUR(binapprox)
    combina.solve()
else:
    print('unknown solver ' + args.solver, file=sys.stderr)
    exit(1)

b_bin_orig = pl.asarray(binapprox.b_bin)

f, (ax1, ax2, ax3) = pl.subplots(3, sharex = True)

ax1.step(t[:-1], b_bin_orig[0,:], label = "b_bin_orig", color = "C0", where = "post")
# ax1.step(t[:-1], b_bin_red[0,:], label = "b_bin_red", color = "C0", linestyle = "dashed", where = "post")
ax1.scatter(t[:-1], b_rel[:,0], label = "b_rel", color = "C0", marker = "x")
ax1.legend(loc = "upper left")
ax1.set_ylabel("b_0")

ax2.step(t[:-1], b_bin_orig[1,:], label = "b_bin_orig", color = "C1", where = "post")
# ax2.step(t[:-1], b_bin_red[1,:], label = "b_bin_red", color = "C1", linestyle = "dashed", where = "post")
ax2.scatter(t[:-1], b_rel[:,1], label = "b_rel", color = "C1", marker = "x")
ax2.legend(loc = "upper left")
ax2.set_ylabel("b_1")

ax3.step(t[:-1], b_bin_orig[2,:], label = "b_bin_orig", color = "C2", where = "post")
# ax3.step(t[:-1], b_bin_red[2,:], label = "b_bin_red", color = "C2", linestyle = "dashed", where = "post")
ax3.scatter(t[:-1], b_rel[:,2], label = "b_rel", color = "C2", marker = "x")
ax3.legend(loc = "lower left")
ax3.set_ylabel("b_2")
ax3.set_xlabel("t")

pl.show()
