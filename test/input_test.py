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
import warnings

import numpy as np

from pycombina._binary_approximation import BinApprox

class InputTest(unittest.TestCase):

    def test_single_control_sos1_violated(self):

        with warnings.catch_warnings(record=True) as w:
            T = np.array([0, 1, 2, 3])
            b_rel = np.array([0.1, 0.3, 0.2])
            BinApprox(T, b_rel)

            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, UserWarning)


    def test_manual_extend_sos1_fulfilled(self):
        for run_idx in range(50):
            num_ctrl = np.random.randint(1, 100)
            num_time = np.random.randint(10, 1000)

            T = np.sort(np.random.rand(num_time))
            b_rel = np.empty((num_ctrl, num_time - 1))
            for i in range(b_rel.shape[0]):
                b_rel[i, :] = (1.0 - b_rel[:i, :].sum(0)) * np.random.rand(num_time - 1)

            with warnings.catch_warnings(record=True) as w:
                BinApprox(T, np.vstack([b_rel, 1.0 - b_rel.sum(0)]))
                self.assertEqual(len(w), 0)


    def test_manual_scale_sos1_fulfilled(self):
        for run_idx in range(50):
            num_ctrl = np.random.randint(2, 100)
            num_time = np.random.randint(10, 1000)

            T = np.sort(np.random.rand(num_time))
            b_rel = np.random.rand(num_ctrl, num_time - 1) / num_ctrl
            b_rel = np.true_divide(b_rel, b_rel.sum(0))

            with warnings.catch_warnings(record=True) as w:
                BinApprox(T, b_rel)
                self.assertEqual(len(w), 0)

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

        self.assertRaises(ValueError, BinApprox, T, b_rel)


    def test_multiple_controls_sos1_violated(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([[0.1, 0.3, 0.3], [0.3, 0.4, 0.5]])

        self.assertRaises(ValueError, BinApprox, T, b_rel)


if __name__ == '__main__':

    unittest.main()

