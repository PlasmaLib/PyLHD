from __future__ import print_function
import numpy as np
import unittest
from PyLHD import eg

class test_eg(unittest.TestCase):
    def test_load_parameters(self):
        eg_data = eg.load('testings/eg_example2d.txt')
        # Assert parameters
        self.assertTrue(eg_data.NAME == 'example-2d')
        self.assertTrue(eg_data.ShotNo == 6115)
        self.assertTrue(eg_data.DimNo == 2)
        self.assertTrue(eg_data.DimName == ['TIME','R'])
        self.assertTrue(eg_data.DimSize == [5,3])
        self.assertTrue(eg_data.DimUnit == ['s','m'])
        self.assertTrue(eg_data.ValNo == 4)
        self.assertTrue(eg_data.ValName == ['a','b','c','d'])
        self.assertTrue(eg_data.ValUnit == ['s','m','V','V'])
        # comments
        self.assertTrue(eg_data.comments['PHI'] == '3.5')
        self.assertTrue(eg_data.comments['PHIunit'] == '\'portNO\'')
        self.assertTrue(eg_data.comments['comments'] == '\'Be thickness = 7.5 micro m\'')


    def test_load_1d(self):
        eg_data = eg.load('testings/eg_example1d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))

    def test_load_1d_variation1(self):
        eg_data = eg.load('testings/eg_example1d_variation1.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME'])
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [0.1,0.2,0.3,0.4,0.5]))

    def test_load_2d(self):
        eg_data = eg.load('testings/eg_example2d.txt')
        # Assert dimname
        self.assertTrue(list(eg_data.dim.keys()) == ['TIME', 'R'])
        # Assert valname
        self.assertTrue(list(eg_data.val.keys()) == ['a', 'b', 'c', 'd'])
        # Assert sizes
        self.assertTrue(eg_data.val['a'].shape == (5,3))
        self.assertTrue(eg_data.dim['TIME'].shape == (5,))
        self.assertTrue(eg_data.dim['R'].shape == (3,))
        # Assert axis
        self.assertTrue(np.allclose(eg_data.dim['TIME'],
                                    [0.01,0.02,0.03,0.04,0.05]))
        self.assertTrue(np.allclose(eg_data.dim['R'],
                                    [0.1,0.2,0.3]))
        # Assert values
        self.assertTrue(np.allclose(eg_data.val['a'],
                                    [[0.11,0.12,0.13],
                                     [0.21,0.22,0.23],
                                     [0.31,0.32,0.33],
                                     [0.41,0.42,0.43],
                                     [0.51,0.52,0.53]]))

    def test_prop(self):
        # test val_property and dim_property
        eg_data = eg.load('testings/eg_example1d.txt')
        val_prop = eg_data.val_property()
        for key in val_prop.keys():
            self.assertTrue(key in ['a','b','c','d'])
            self.assertTrue(val_prop[key] in ['s','m','V','V'])
        dim_prop = eg_data.dim_property()
        for key in dim_prop.keys():
            self.assertTrue(key in ['TIME'])
            self.assertTrue(dim_prop[key] in ['s'])

    def test_slice(self):
        # Make sure EGdata.__getitem__ certainly works.
        eg_data = eg.load('testings/eg_example2d.txt')
        eg_a_original = eg_data.val['a'].copy()
        eg_R_original = eg_data.dim['R'].copy()
        # crop by axis=0
        crop = eg_data[1:3]
        self.assertTrue(np.allclose(crop.dim['TIME'], [0.02,0.03]))
        self.assertTrue(np.allclose(crop.dim['R'], eg_data.dim['R']))
        self.assertTrue(np.allclose(crop.val['a'], eg_data.val['a'][1:3]))
        # make sure eg_data is not changed
        self.assertTrue(np.allclose(eg_R_original, eg_data.dim['R']))
        self.assertTrue(np.allclose(eg_a_original, eg_data.val['a']))

    def test_index(self):
        # Make sure EGdata.__getitem__ certainly works.
        eg_data = eg.load('testings/eg_example2d.txt')
        eg_a_original = eg_data.val['a'].copy()
        eg_R_original = eg_data.dim['R'].copy()
        # crop by axis=0
        crop = eg_data[[1,2]]
        self.assertTrue(np.allclose(crop.dim['TIME'], [0.02,0.03]))
        self.assertTrue(np.allclose(crop.dim['R'], eg_data.dim['R']))
        self.assertTrue(np.allclose(crop.val['a'], eg_data.val['a'][1:3]))
        # make sure eg_data is not changed
        self.assertTrue(np.allclose(eg_R_original, eg_data.dim['R']))
        self.assertTrue(np.allclose(eg_a_original, eg_data.val['a']))

    def test_dump_2d(self):
        #eg_data = eg.load('testings/eg_example2d.txt')
        #eg_data.dump('testings/eg_example2d_dump.txt')
        pass


if __name__ == '__main__':
     unittest.main()
