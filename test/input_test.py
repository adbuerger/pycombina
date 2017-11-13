import unittest

from pycombina import CIA, CIA_SCIP

class InputValid(unittest.TestCase):

    def setUp(self):

        self.T = [0, 1, 2, 3]
        self.b_rel = [0.1, 0.3, 0.2]


    def test_input_valid_cia(self):

        cia = CIA(self.T, self.b_rel)

        
    def test_input_valid_cia_scip(self):

        cia_scip = CIA_SCIP(self.T, self.b_rel)


class InputInvalidDimensions(unittest.TestCase):

    def setUp(self):

        self.T = [0, 1, 2, 3]
        self.b_rel = [0.1, 0.3, 0.2, 0.5]


    def test_input_invalid_dimensions_cia(self):

        self.assertRaises(ValueError, CIA, self.T, self.b_rel)


    def test_input_invalid_dimensions_cia_scip(self):

        self.assertRaises(ValueError, CIA_SCIP, self.T, self.b_rel)

        
class InputInvalidT(unittest.TestCase):

    def setUp(self):

        self.T = [0, 2, 1, 3]
        self.b_rel = [0.1, 0.3, 0.2]


    def test_input_invalid_T_cia(self):

        self.assertRaises(ValueError, CIA, self.T, self.b_rel)


    def test_input_invalid_T_cia_scip(self):

        self.assertRaises(ValueError, CIA_SCIP, self.T, self.b_rel)


class InputInvalidBRel(unittest.TestCase):

    def setUp(self):

        self.T = [0, 2, 1, 3]
        self.b_rel = [0.1, 0.3, 1.2]


    def test_input_invalid_b_rel_cia(self):

        self.assertRaises(ValueError, CIA, self.T, self.b_rel)


    def test_input_invalid_b_rel_cia_scip(self):

        self.assertRaises(ValueError, CIA_SCIP, self.T, self.b_rel)


if __name__ == '__main__':

    unittest.main()

