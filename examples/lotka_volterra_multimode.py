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

import pylab as pl
import pycombina

pl.close("all")

data = pl.loadtxt("data/mmlotka_nt_12000_400.csv", delimiter=" ", skiprows=1)

dN = 1

t = data[::dN,0]
b_rel = data[:-1:dN, 3:]

max_switches = [5, 2, 3]

binapprox = pycombina.BinApprox(t=t, b_rel=b_rel, binary_threshold=1e-3)

binapprox.set_n_max_switches(n_max_switches=max_switches)
# binapprox.set_valid_controls_for_interval((0, 2), [0,0,1])
#binapprox.set_valid_control_transitions(0, [1,0,1])
#binapprox.set_min_up_times([2.0, 2.0, 2.0])
#binapprox.set_cia_norm("row_sum_norm")

combina = pycombina.CombinaBnB(binapprox)
combina.solve(max_iter= int(5e6), max_cpu_time=3.6e3)

b_bin = pl.asarray(binapprox.b_bin)

f, (ax1, ax2, ax3) = pl.subplots(3, sharex = True)

ax1.step(t[:-1], b_bin[0,:], label="b_bin_orig", color="C0", where="post")
ax1.scatter(t[:-1], b_rel[:,0], label="b_rel", color="C0", marker="x")
ax1.legend(loc="upper left")
ax1.set_ylabel("b_0")

ax2.step(t[:-1], b_bin[1,:], label="b_bin_orig", color="C1", where="post")
ax2.scatter(t[:-1], b_rel[:,1], label="b_rel", color="C1", marker="x")
ax2.legend(loc="upper left")
ax2.set_ylabel("b_1")

ax3.step(t[:-1], b_bin[2,:], label="b_bin_orig", color="C2", where="post")
ax3.scatter(t[:-1], b_rel[:,2], label="b_rel", color="C2", marker="x")
ax3.legend(loc="lower left")
ax3.set_ylabel("b_2")
ax3.set_xlabel("t")

pl.show()
