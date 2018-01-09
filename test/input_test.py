import unittest
import numpy as np

from pycombina._combina import Combina

class InputTest(unittest.TestCase):

    def test_input_valid(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        Combina(T, b_rel)


    def test_input_invalid_dimensions(self):

        T = np.array([0, 1, 2, 3])
        b_rel = np.array([0.1, 0.3, 0.2, 0.5])

        self.assertRaises(ValueError, Combina, T, b_rel)

        
    def test_input_T_not_increasing(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 0.2])

        self.assertRaises(ValueError, Combina, T, b_rel)


    def test_input_b_rel_not_relaxed_binary_solution(self):

        T = np.array([0, 2, 1, 3])
        b_rel = np.array([0.1, 0.3, 1.2])

        self.assertRaises(ValueError, Combina, T, b_rel)


if __name__ == '__main__':

    unittest.main()

