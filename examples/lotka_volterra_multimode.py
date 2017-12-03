#!/usr/bin/python

import pylab as pl
from pycombina import Combina

# pl.close("all")

data = pl.loadtxt("data/mmlotka_nt_12000_400.csv", delimiter = " ", skiprows = 1)

dN = 80

T = data[::dN,0].tolist()
b_rel = data[:-1:dN, 3:].T.tolist()

max_switches = [2, 2, 2]

combina = Combina(T, b_rel)
combina.solve(solver = "bnb", max_switches = max_switches)
b_bin = combina.b_bin


f, (ax1, ax2, ax3) = pl.subplots(3, sharex = True)
ax1.step(combina.T[:-1], b_bin[0], color = "r", where = "post")
ax1.scatter(T[:-1], b_rel[0], color = "r", marker = "x")
ax2.step(combina.T[:-1], b_bin[1], color = "g", where = "post")
ax2.scatter(T[:-1], b_rel[1], color = "g", marker = "x")
ax3.step(combina.T[:-1], b_bin[2], color = "b", where = "post")
ax3.scatter(T[:-1], b_rel[2], color = "b", marker = "x")
pl.show()
