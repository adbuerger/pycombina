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

import glob

from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

# Set up extension module.
setup(
    ext_modules=[
        Pybind11Extension(
            name="pycombina._combina_bnb_solver",
            sources=[
                *glob.glob("src/combina_bnb_solver/*.cpp"),
                *glob.glob("src/combina_bnb_solver/**/*.cpp"),
            ],
        ),
    ]
)
