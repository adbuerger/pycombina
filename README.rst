.. image:: logo/logo.png

pycombina - Combinatorial Integral Approximation
================================================

|gitlab-ci|

.. |gitlab-ci| image:: https://www.w.hs-karlsruhe.de/gitlab/ab/pycombina/badges/master/pipeline.svg
    :target: https://www.w.hs-karlsruhe.de/gitlab/ab/pycombina/commits/master
    :alt: Gitlab CI pipeline status master branch

**pycombina** is a Python module for solving combinatorial integral approximation problems.

Combinatorial integral approximation problems can be formulated and solved

1. by a custom Branch-and-Bound algorithm (using fast implementation in C++, recommended),
2. by SCIP (using an MILP formulation, requires SCIP and pyscipopt)
3. by Gurobi (using an MILP formulation, requires Gurobi and gurobipy)

while the problem setup is widely automatized.

For more information on the implemented algorithms, see, e. g., [#f1]_.


Prerequisites
-------------

pycombina has been tested with Python2.7 on Ubuntu 16.04. 

Python modules
~~~~~~~~~~~~~~

The following Python modules are required:

- ``setuptools``
- ``unittest2`` (optional, for running automated tests)
- ``numpy`` (optional, for running automated tests)
- ``pyscipopt`` (optional, required for using SCIP (solver license required), see [#f2]_ and [#f3]_)
- ``gurobipy`` (optional, required for using Gurobi (solver license required), see  [#f4]_)


Other software
~~~~~~~~~~~~~~

For building the C++ implementation, the following packages are required

- ``python-dev``
- ``g++``
- ``cmake``

**Please note:** pycombina uses features available only from C++11 on and uses pybind11 [#f5]_ (a copy of pybind11 is shipped with pycombina).


How to install
--------------

For system-wide installation of the Python module, run

.. code-block:: bash

   sudo python setup.py install


If you're working on the module, it's better to just set a link
to the containing folder, which can be done by running

.. code-block:: bash

   sudo python setup.py develop


To run the the automated tests, run

.. code-block:: bash

   python setup.py test


Tests for SCIP and Gurobi will be skipped automatically if they're not available.


How to use
----------

For examples on how to use the module, please refer to the tests.


.. rubric:: References

.. [#f1] |linkf1|_

.. _linkf1: https://mathopt.de/Sager/publications.php

.. |linkf1| replace:: Sager et al.: Combinatorial Integral Approximation. *Mathematical Methods of Operations Research*, 2011


.. [#f2] |linkf2|_

.. _linkf2: https://github.com/SCIP-Interfaces/PySCIPOpt

.. |linkf2| replace:: PySCIPOpt - Python interface for the SCIP Optimization Suite (website)


.. [#f3] |linkf3|_

.. _linkf3: http://scip.zib.de/

.. |linkf3| replace:: SCIP - Solving Constraint Integer Programs (website)


.. [#f4] |linkf4|_

.. _linkf4: http://www.gurobi.com/documentation/6.5/quickstart_mac/the_gurobi_python_interfac.html

.. |linkf4| replace:: The Gurobi Python Interface for Python Users (website)


.. [#f5] |linkf5|_

.. _linkf5: https://github.com/pybind/pybind11

.. |linkf5| replace:: pybind11 - Seamless operability between C++11 and Python (website)
