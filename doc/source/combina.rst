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


Combinatorial integral approximation
====================================

[Here goes a short description of what combinatorial integral approximation is, what is it used to and where it ca be applied]

tbd


Problem formulation
-------------------

Given a matrix :math:`b_\mathrm{rel} \in [0,1]^{n_\mathrm{c} \times n_\mathrm{r}}` which corresponds to the relaxed solution of :math:`n_\mathrm{c}` binary variables at :math:`n_\mathrm{b}` control intervals and a vector of time points :math:`t \in \mathbb{R}^{n_\mathrm{b}+1}` with :math:`t_{k+1} - t_k > 0` for :math:`k=0,\dots,n_\mathrm{b}`. With :math:`\sigma_{\mathrm{max},k} \in \mathrm{N}^{n_\mathrm{c}}`, pycombina can be use to solve a combinatorial integral approximation problem of the following form

.. math::
    
    \begin{aligned}
    \underset{b_\mathrm{bin}}{\mathrm{min}} \hspace{0.2cm} \underset{k=1,\dots,n_\mathrm{c}}{\mathrm{max}} \hspace{0.2cm} \underset{i=1,\dots,n_\mathrm{b}}{\mathrm{max}} & \hspace{0.2cm}  \left| \sum_{j=1}^{i} (b_{\mathrm{rel},k,j} - b_{\mathrm{bin},k,j})\cdot (t_{k+1}-t_k) \right| \\
    \mathrm{subject~to} & \hspace{0.2cm} \sum_{i=1}^{n_\mathrm{b}-1} |b_{\mathrm{bin},k,i} - b_{\mathrm{bin},k,i+1}| \leq  \sigma_{k,\mathrm{max}}, \quad k = 1,\dots,n_\mathrm{c}, \\
    & \hspace{0.2cm} \sum_{k=1}^{n_\mathrm{c}} b_{\mathrm{bin},k,i} \leq 1, \quad i = 1,\dots,n_\mathrm{b} \\
    & \hspace{0.2cm} b_{\mathrm{bin},k,i} \in \{ 0, 1 \}, \quad i = 1,\dots,n_\mathrm{b},~k = 1,\dots,n_\mathrm{c}.
    \end{aligned}


Problem solution using pycombina
--------------------------------

Given numpy arrays for `b_rel` and `t` in accordance to the problem formulation above, a combinatorial integral approximation problem can be instantiated from the class ``pycombina.Combina``. The problem can then be solved using the class function ``solve()``, where ``sigma_max`` can be specified as well as the desired solution method/solver:

   * `bnb` - solve using a custom Branch-and-Bound algorithm (recommended)
   * `scip` - solve using SCIP (MILP formulation, requires SCIP and pyscipopt)
   * `gurobi` - solve using Gurobi (MILP formulation, requires Gurobi and gurobipy)


For more information on algorithms and formulations, see [#f1]_.

.. note::

   Running pycombia for large dimensions of :math:`b_\mathrm{rel}` and/or bigger values in :math:`\sigma_\mathrm{max}` might results in high solution times and memory consumption due to exponentially increasing problem complexity.


Preprocessing
-------------

[Once implemented, there goes information on the preprocessing heuristics]

tbd


Description of the class ``pycombina.Combina``
----------------------------------------------

.. autoclass:: pycombina.Combina
    :members:
    :inherited-members:


.. rubric:: References

.. [#f1] |linkf1|_

.. _linkf1: https://mathopt.de/Sager/publications.php

.. |linkf1| replace:: Sager et al.: Combinatorial Integral Approximation. *Mathematical Methods of Operations Research*, 2011
