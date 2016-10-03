import numpy as np
import collections
from . import eg

class load_cxsimg(loadtxt):
    '''
    class that manipulating lhdcxs6_img or lhdcxs7_img
    '''
    def __init__(self, filename):
        # loading txt
        loadtxt.__init__(self, filename)
        # variables for sorting
        self.radius={}
        self.array={}
        self.port={}
        for val in self.Valname:
            if '_' in val:
                self.radius[val] = val[:val.find('_')]
                self.array[val]  = val[val.find('(')+1:val.find('-')]
                self.port[val]   = val[val.find('-')+1:val.find(')')]

    def getKeysFromArray(self, array):
        keys = []
        for key in self.array.keys():
            if self.array[key] == str(array):
                keys.append(key)
        return keys
