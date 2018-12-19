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

.. pycombina documentation master file, created by
.. sphinx-quickstart on Mon Dec  8 09:36:29 2014.
.. You can adapt this file completely to your liking, but it should at least
.. contain the root `toctree` directive.


.. image:: ../../logo/logo.png

|

**pycombina** is a Python module for solving binary approximation problems.

Multi-dimensional binary approximation problems can be formulated including
a variety of combinatorial constraints (such as maximum number of switches,
dwell times and switching adjacencies) and solved using different methods.

|travis-ci| |rtd|

.. |travis-ci| image:: https://travis-ci.org/adbuerger/pycombina.svg?branch=master
    :target: https://travis-ci.org/adbuerger/pycombina
    :alt: Travis CI pipeline status master branch

.. |rtd| image:: https://readthedocs.org/projects/pycombina/badge/?version=latest
    :target: https://pycombina.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Contents

   install
   binapprox
   rounding
   combina
   pycombina_sample_application
   