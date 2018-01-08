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


How to install
==============

pycombina has been tested with Python2.7 on Ubuntu 16.04. 

Required Python modules
-----------------------

The following Python modules are required:

- ``setuptools``
- ``unittest2`` (optional, for running automated tests)
- ``numpy`` (optional, for running automated tests)
- ``pyscipopt`` (optional, required for using SCIP (solver license required), see [#f2]_ and [#f3]_)
- ``gurobipy`` (optional, required for using Gurobi (solver license required), see  [#f4]_)


Required build software
-----------------------

For building the C++ implementation, the following packages are required

- ``python-dev``
- ``g++``
- ``cmake``

**Please note:** pycombina uses features available only from C++11 on and uses pybind11 [#f5]_ (a copy of pybind11 is shipped with pycombina).


Installation
------------

For system-wide installation of the Python module, run

.. code-block:: bash

   sudo python setup.py install


If you're working on development of the module, it's better to just set a link
to the containing folder, which can be done by running

.. code-block:: bash

   sudo python setup.py develop


To run the the automated tests, run

.. code-block:: bash

   python setup.py test


Tests for SCIP and Gurobi will be skipped automatically if they're not available.

.. rubric:: References

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
