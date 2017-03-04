from __future__ import print_function
import numpy as np
import unittest
from future.moves.urllib.request import urlopen, Request
from future.moves.urllib.error import URLError
import socket
try:
    from PyLHD import pgdb
    class test_eg(unittest.TestCase):
        def test_load_parameters(self):
            try:
                urlopen('http://kaiseki-dev.lhd.nifs.ac.jp/software/shotsummary/Main_new.htm', timeout=1)
                print('connected to server')
                rslt = pgdb.load(110000, ['MagneticField'])
                # make sure it indicates true values
                self.assertTrue(rslt['MagneticField']==-0.9)
            except socket.timeout:
                print('timed out')
            except URLError:
                print('timed out')

except ImportError:
    pass

if __name__ == '__main__':
     unittest.main()
