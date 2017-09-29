import unittest

from pycombina import CIA

class InputTest(unittest.TestCase):

    def test_input_valid(self):

        T = [0, 1, 2, 3]
        b_rel = [0.1, 0.3, 0.2]
        
        cia = CIA(T, b_rel)


    def test_input_invalid_dimensions(self):

        T = [0, 1, 2, 3]
        b_rel = [0.1, 0.3, 0.2, 0.5]
        
        self.assertRaises(ValueError, CIA, T, b_rel)


    def test_input_invalid_T(self):

        T = [0, 2, 1, 3]
        b_rel = [0.1, 0.3, 0.2]
        
        self.assertRaises(ValueError, CIA, T, b_rel)


    def test_input_invalid_b_rel(self):

        T = [0, 2, 1, 3]
        b_rel = [0.1, 0.3, 1.2]
        
        self.assertRaises(ValueError, CIA, T, b_rel)


if __name__ == '__main__':

    unittest.main()

