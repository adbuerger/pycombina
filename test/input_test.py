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

from pycombina._binary_approximation import BinApprox

class InputTest(unittest.TestCase):

    def test_single_control_sos1_fulfilled(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        BinApprox(T, b_rel, off_state_included = False)


    def test_single_control_sos1_violated(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        self.assertRaises(ValueError, BinApprox, T, b_rel, off_state_included = True)


    def test_single_control_invalid_dimensions(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2, 0.5])

        self.assertRaises(ValueError, BinApprox, T, b_rel)

        
    def test_single_control_T_not_increasing(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        self.assertRaises(ValueError, BinApprox, T, b_rel)


    def test_single_control_b_rel_not_relaxed_binary_solution(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 1.2])

        self.assertRaises(ValueError, BinApprox, T, b_rel)


    def test_multiple_controls_sos1_fulfilled_manual(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([[0.1, 0.3, 0.3], [0.9, 0.7, 0.7]])

        self.assertRaises(ValueError, BinApprox, T, b_rel, off_state_included = True)


    def test_multiple_controls_sos1_fulfilled_auto(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([[0.1, 0.3, 0.3], [0.2, 0.4, 0.5]])

        self.assertRaises(ValueError, BinApprox, T, b_rel, off_state_included = False)


    def test_multiple_controls_sos1_violated(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([[0.1, 0.3, 0.3], [0.3, 0.4, 0.5]])

        self.assertRaises(ValueError, BinApprox, T, b_rel,  off_state_included = True)


if __name__ == '__main__':

    unittest.main()

