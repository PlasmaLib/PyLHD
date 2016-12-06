from __future__ import print_function
import numpy as np
import unittest
from PyLHD import pgdb

class test_eg(unittest.TestCase):
    def test_load_parameters(self):
        rslt = pgdb.load(110000, ['MagneticField'])
        print(rslt)

if __name__ == '__main__':
     unittest.main()
