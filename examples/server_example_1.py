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
import requests

pl.close("all")

data = pl.loadtxt("data/data_example_1.csv", delimiter = " ", skiprows = 1)

t = data[:,0]
b_rel = data[:-1, 1]
n_max_switches = [4]

server_address = "http://localhost:6789/api/solve/"

problem_definition = {
    
    "t": t.tolist(),
    "b_rel": b_rel.tolist(),
    "off_state_included": False,

    "n_max_switches": n_max_switches,
    "solver": "CombinaBnB"
}

r = requests.post(server_address, json = problem_definition)

print("Status:", r.status_code)

solution = r.json()

print("Errors:", solution["errors"])

print("Solver:", solution["solver"])
print("Solver status:", solution["solver_status"])
print("Objective value:", solution["eta"])

if r.status_code == 200:

    b_bin = pl.squeeze(r.json()["b_bin"])

    pl.figure()
    pl.step(t[:-1], b_rel, label = "b_rel", color = "C0", linestyle = "dashed", where = "post")
    pl.step(t[:-1], b_bin, label = "b_bin", color = "C0", where = "post")
    pl.xlabel("t")
    pl.ylabel("b")
    pl.legend(loc = "upper left")
    pl.show()
