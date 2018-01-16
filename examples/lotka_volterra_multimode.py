#!/usr/bin/python

import pylab as pl
from pycombina import Combina

# pl.close("all")

data = pl.loadtxt("data/mmlotka_nt_12000_400.csv", delimiter = " ", skiprows = 1)

dN = 80

t = data[::dN,0]
b_rel = data[:-1:dN, 3:]

max_switches = [2, 2, 2]

combina = Combina(t, b_rel)
combina.solve(solver = "bnb", max_switches = max_switches)
b_bin_full = combina.b_bin

combina.reduce_problem_size(max_reduction = True)
combina.solve(solver = "bnb", max_switches = max_switches)
b_bin_red = combina.b_bin

f, (ax1, ax2, ax3) = pl.subplots(3, sharex = True)
ax1.step(combina.t[:-1], b_bin_full[0,:], color = "r", where = "post")
ax1.scatter(t[:-1], b_bin_red[0,:], color = "r", marker = "x")
ax1.scatter(t[:-1], b_rel[:,0], color = "k", marker = "x")
ax2.step(combina.t[:-1], b_bin_full[1,:], color = "g", where = "post")
ax2.scatter(t[:-1], b_bin_red[1,:], color = "g", marker = "x")
ax2.scatter(t[:-1], b_rel[:,1], color = "k", marker = "x")
ax3.step(combina.t[:-1], b_bin_full[2,:], color = "b", where = "post")
ax3.scatter(t[:-1], b_bin_red[2,:], color = "b", marker = "x")
ax3.scatter(t[:-1], b_rel[:,2], color = "k", marker = "x")
pl.show()
