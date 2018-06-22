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

import unittest
import numpy as np

from mock import patch

from pycombina._binary_approximation import BinaryApproximationBaseClass

class InputTest(unittest.TestCase):

    @patch.multiple(BinaryApproximationBaseClass, __abstractmethods__=set())
    def test_input_valid(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        BinaryApproximationBaseClass(T, b_rel)


    @patch.multiple(BinaryApproximationBaseClass, __abstractmethods__=set())
    def test_input_invalid_dimensions(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2, 0.5])

        self.assertRaises(ValueError, BinaryApproximationBaseClass, T, b_rel)

        
    @patch.multiple(BinaryApproximationBaseClass, __abstractmethods__=set())
    def test_input_T_not_increasing(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        self.assertRaises(ValueError, BinaryApproximationBaseClass, T, b_rel)


    @patch.multiple(BinaryApproximationBaseClass, __abstractmethods__=set())
    def test_input_b_rel_not_relaxed_binary_solution(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 1.2])

        self.assertRaises(ValueError, BinaryApproximationBaseClass, T, b_rel)


if __name__ == '__main__':

    unittest.main()

