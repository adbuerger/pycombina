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
from pycombina import BinApprox, CombinaBnB, CombinaMILP, CombinaSUR


# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--max_switches', type=int, default=4, help='maximal number of control switches allowed')
subparsers = parser.add_subparsers(help='solver choice')
parser_bnb = subparsers.add_parser('bnb', help='Combina Branch-and-Bound solver')
parser_bnb.add_argument('--search_strategy', type=str, default='dfs', choices=['bfs', 'dfs', 'dbt'], help='tree search strategy')
parser_bnb.add_argument('--dbt_beta', metavar='F', type=float, default=0.5, help='parameter for dynamic backtracking')
parser_bnb.add_argument('--max_iter', metavar='N', type=int, default=5000000, help='maximal number of branch-and-bound iterations')
parser_bnb.set_defaults(solver='bnb')
parser_milp = subparsers.add_parser('milp', help='Generic MILP solver')
parser_milp.add_argument('--time_limit', type=float, default=20.0, help='run time limit in seconds')
parser_milp.add_argument('--mip_gap', type=float, default=0.8, help='target MIP gap')
parser_milp.set_defaults(solver='milp')
parser_sur = subparsers.add_parser('sur', help='Sum up rounding solver')
parser_sur.set_defaults(solver='sur')
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
    combina = CombinaBnB(binapprox)
    combina.solve(use_warm_start=False, bnb_search_strategy=args.search_strategy, bnb_opts={'dbt_beta': args.dbt_beta, 'max_iter': args.max_iter})
elif args.solver == 'milp':
    combina = CombinaMILP(binapprox)
    combina.solve(gurobi_opts = {"TimeLimit": args.time_limit, "MIPGap": args.mip_gap})
else:
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
