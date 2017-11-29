#!/usr/bin/python

import pylab as pl
from pycombina import Combina

pl.close("all")

data = pl.loadtxt("data/mmlotka_nt_12000_400.csv", delimiter = " ", skiprows = 1)

dN = 80

T = data[::dN,0].tolist()
b_rel = data[:-1:dN, 3:].T.tolist()

sigma_max = [2, 4, 6]

combina = Combina(T, b_rel)
combina.solve(sigma_max, solver = "bnb")
b_bin = combina.b_bin


eta = [0, 0, 0]
Tg = (pl.asarray(T[1:]) - pl.asarray(T[:-1])).tolist()

for k, b_bin_k in enumerate(b_bin):

    for i, b_i in enumerate(b_bin_k):

        eta_i = abs(sum([Tg[j] * (b_rel[k][j] - b_bin_k[j]) for j in range(i)]))

        if eta_i > eta[k]:

            eta[k] = eta_i


f, (ax1, ax2, ax3) = pl.subplots(3, sharex = True)
ax1.step(T[:-1], b_bin[0], color = "r")
ax1.step(T[:-1], b_rel[0], color = "r", linestyle = "dashed")
ax2.step(T[:-1], b_bin[1], color = "g")
ax2.step(T[:-1], b_rel[1], color = "g", linestyle = "dashed")
ax3.step(T[:-1], b_bin[2], color = "b")
ax3.step(T[:-1], b_rel[2], color = "b", linestyle = "dashed")
pl.show()
