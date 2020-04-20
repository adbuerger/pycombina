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

import pycombina
from pycombina import BinApprox

# parse command line arguments
parser = ap.ArgumentParser()
parser.add_argument('--max_switches', metavar='count', type=int, nargs=3, default=[5, 2, 3], help='specify maximum number of switches')
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
