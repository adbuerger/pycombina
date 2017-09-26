import unittest

from pycombina import cia

class InputTest(unittest.TestCase):

    def test_invalid_input(self):

        b_rel = [9.164991131439303e-08, 9.164989910069793e-08, 3.2]
        sigma_max = 4
        
        self.assertRaises(ValueError, cia, b_rel, sigma_max)


if __name__ == '__main__':

    unittest.main()

