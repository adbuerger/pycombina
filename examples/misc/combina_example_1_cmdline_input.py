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
parser.add_argument(
    '--max_switches', type=int, default=4, metavar='count',
    help='maximal number of control switches allowed'
)
parser.add_argument(
    '--solver', type=str, choices=['bnb', 'milp', 'sur'], default='bnb',
    metavar='name', help='specify solver for CIA problem'
)

if hasattr(pycombina, 'CombinaBnB'):
    bnb_group = parser.add_argument_group('Branch-and-Bound arguments')
    bnb_group.add_argument(
        '--strategy', type=str, default=None, metavar='name',
        choices=pycombina.CombinaBnB.get_search_strategies(),
        help='specify tree search strategy'
    )
    bnb_group.add_argument(
        '--max_iter', type=int, default=None, metavar='count',
        help='maximum number of branch-and-bound iterations'
    )
    bnb_group.add_argument(
        '--max_cpu_time', type=float, default=None, metavar='secs',
        help='maximum number of CPU seconds'
    )
    bnb_group.add_argument(
        '--vbc_file', type=str, default=None, metavar='file',
        help='path for VBC output'
    )
    bnb_group.add_argument(
        '--vbc_time_dilation', type=float, default=None, metavar='factor',
        help='stretch times in VBC file by fixed factor'
    )

    timing_args = bnb_group.add_mutually_exclusive_group()
    timing_args.add_argument(
        '--vbc_timing', dest='vbc_timing', action='store_true',
        help='include timing information in VBC output'
    )
    timing_args.add_argument(
        '--no_vbc_timing', dest='vbc_timing', action='store_false',
        help='remove timing information from VBC output'
    )
    timing_args.set_defaults(vbc_timing=None)
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
    # Create CombinaBnB solver object
    from pycombina import CombinaBnB
    combina = CombinaBnB(binapprox)

    # Read keyword arguments
    kwargs = {}
    if args.strategy is not None:
        kwargs['strategy'] = args.strategy
    if args.max_iter is not None:
        kwargs['max_iter'] = args.max_iter
    if args.max_cpu_time is not None:
        kwargs['max_cpu_time'] = args.max_cpu_time
    if args.vbc_file is not None:
        kwargs['vbc_file'] = args.vbc_file
    if args.vbc_timing is not None:
        kwargs['vbc_timing'] = args.vbc_timing
    if args.vbc_time_dilation is not None:
        kwargs['vbc_time_dilation'] = args.vbc_time_dilation

    # Invoke solver
    combina.solve(use_warm_start=False, **kwargs)
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
