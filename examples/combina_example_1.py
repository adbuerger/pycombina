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

data = pl.loadtxt("data/data_example_1.csv", delimiter=" ", skiprows=1)

t = data[:,0]
b_rel = data[:-1, 1]
max_switches = [4]

binapprox = pycombina.BinApprox(t=t, b_rel=b_rel, \
    binary_threshold=1e-3, off_state_included=False)

binapprox.set_n_max_switches(n_max_switches=max_switches)

combina = pycombina.CombinaBnB(binapprox)
combina.solve(verbosity=2)

b_bin = pl.squeeze(binapprox.b_bin)

pl.figure()
pl.step(t[:-1], b_rel, label="b_rel", color="C0", linestyle="dashed", where="post")
pl.step(t[:-1], b_bin, label="b_bin", color="C0", where="post")
pl.xlabel("t")
pl.ylabel("b")
pl.legend(loc="upper left")
pl.show()
