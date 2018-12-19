.. This file is part of pycombina.
..
.. Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
..
.. pycombina is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Lesser General Public License as published by
.. the Free Software Foundation, either version 3 of the License, or
.. (at your option) any later version.
..
.. pycombina is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
.. GNU Lesser General Public License for more details.
..
.. You should have received a copy of the GNU Lesser General Public License
.. along with pycombina. If not, see <http://www.gnu.org/licenses/>.


Binary approximation problems
=============================

**pycombina** can solve binary approximation problems as they arise, e. g., within efficient solution of Mixed Integer Optimal Control Problems (MIOCPs), using different methods such as Sum-Up-Rounding or Combinatorial Integral Approximation [#f1]_.

Prior to solving, a binary approximation problem has to be formulated using :class:`pycombina.BinApprox`. The resulting object can then later be passed to one of the solvers contained in **pycombina**.

.. autoclass:: pycombina._binary_approximation.BinApprox
    :members:
    :inherited-members:

.. rubric:: References

.. [#f1] |linkf1|_

.. _linkf1: https://mathopt.de/Sager/publications.php

.. |linkf1| replace:: Sager et al.: Combinatorial Integral Approximation. *Mathematical Methods of Operations Research*, 2011
