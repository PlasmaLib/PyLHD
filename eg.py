'''
A function that reads eg file for the LHD experiment.
The typical usage is 

>>> data = eg.loadtxt(filename)

The dimension data is stored in self.dim (ordered dict), while the data are 
stored self.val (ordered dict)

To check the contents,

>>> data.dim.keys()
(equivalently data.dim_keys())

>>> data.val.keys()
(equivalently data.val_keys())

To access the data, 

>>> data.dim[key]

>>> data.val[key]

can be used.

Created on Mar 28, 2016

@author: keisukefujii
'''

import numpy as np
import collections

class loadtxt(object):
    '''
    Class for manipulating eg file
    '''
    def __init__(self, filename):
        '''
        Constructor
        '''
        self.comments = collections.OrderedDict()
        for line in open(filename, 'r'):
            # reading DimNo
            if '# DimNo '.lower() in line.lower():
                self.DimNo = int(line[line.find('=')+1:].strip().replace("'", ""))
            # reading DimName
            elif '# DimName '.lower() in line.lower():
                self.DimName = [s.strip().replace("'", "") for s in line[line.find('=')+1:].split(',')]
            # reading DimSize
            elif '# DimSize '.lower() in line.lower():
                self.DimSize = [int(s.strip().replace("'", "")) for s in line[line.find('=')+1:].split(',')]
            # reading DimUnit
            elif '# DimUnit '.lower() in line.lower():
                self.DimUnit = [s.strip().replace("'", "") for s in line[line.find('=')+1:].split(',')]
            # reading Name
            elif '# Name '.lower() in line.lower():
                self.Name = line[line.find('=')+1:].strip().replace("'", "")
            # reading shot number
            elif '# ShotNo '.lower() in line.lower():
                try:
                    self.ShotNo = int(line[line.find('=')+1:].strip().replace("'", ""))
                except:
                    pass
            # reading Date
            elif '# Date '.lower() in line.lower():
                self.Date = line[line.find('=')+1:].strip().replace("'", "")
            # reading DimNo
            elif '# ValNo '.lower() in line.lower():
                self.ValNo = int(line[line.find('=')+1:].strip().replace("'", ""))
            # reading ValName
            elif '# Valname '.lower() in line.lower():
                self.Valname = [s.strip().replace("'", "") for s in line[line.find('=')+1:].split(',')]
            # reading ValName
            elif '# ValUnit '.lower() in line.lower():
                self.ValUnit = [s.strip().replace("'", "") for s in line[line.find('=')+1:].split(',')]
            # reading comment
            elif '#' in line:
                key = line[line.find('#')+1:line.find("=")].strip()
                comment = line[line.find('=')+1:]
                self.comments[key] = comment
            else:
                break
        # temporary data
        tmpdata = np.loadtxt(filename, comments='#', delimiter=',')

        # preparing dict         
        self.dim = collections.OrderedDict()
        self.val = collections.OrderedDict()
        for dim in self.DimName:
            self.dim[dim] = np.zeros(self.DimSize).flatten()
        for val in self.Valname:
            self.val[val] = np.zeros(self.DimSize).flatten()
             
        # storing into data (dict)
        for l in range(len(tmpdata)):
            for i in range(len(tmpdata[l])):
                if i < self.DimNo:
                    self.dim[self.DimName[i]][l] = tmpdata[l][i]
                else:
                    self.val[self.Valname[i-self.DimNo]][l] = tmpdata[l][i]
        
        # reshaping vals
        for val in self.Valname:
            self.val[val] = np.array(self.val[val]).reshape(self.DimSize)
            
        # reshaping dims
        for i in range(len(self.DimName)):
            dim = self.DimName[i]
            self.dim[dim] = np.array(self.dim[dim]).reshape(self.DimSize)
            
        # TODO for more dimensional data
        if len(self.DimName) == 2:
            self.dim[self.DimName[0]] = self.dim[self.DimName[0]][:,0] 
            self.dim[self.DimName[1]] = self.dim[self.DimName[1]][0,:] 
        elif len(self.DimName) == 3:
            self.dim[self.DimName[0]] = self.dim[self.DimName[0]][:,0,0] 
            self.dim[self.DimName[1]] = self.dim[self.DimName[1]][0,:,0] 
            self.dim[self.DimName[2]] = self.dim[self.DimName[2]][0,0,:] 
        elif len(self.DimName) > 3:
            raise ValueError('4 or more dimensional is not currently supported. The data dimension:'+str(len(self.DimName)), self.DimName)
        
        
    def dim_keys(self):
        return self.dim.keys() 
    
    def val_keys(self):
        return self.val.keys()
    
    def keys(self):
        return {'dim_keys': self.dim_keys(), 'val_keys': self.val_keys()}
    
    def getDim(self, index):
        return self.dim[self.DimName[index]]
    
    def getVal(self, index):
        return self.val[self.Valname[index]]
    
    def crop(self, index, axis=0):
        """
        Cropping the original data and through the rest away.
        :param index: The cropping indices. The data[index_start] will be kept.
        :param axis: The axis where the cropping should be applied.
        :return : The cloned eg_data
        """
        # for val
        for key,item in self.val.items():
            if axis==0:
                self.val[key] = item[index,:]
            elif axis==1:
                self.val[key] = item[:,index]
            elif axis==2:
                self.val[key] = item[:,:,index]
        # for dim
        dim_key = self.dim_keys()[axis]
        self.dim[dim_key] = self.dim[dim_key][index]
        # for DimSize
        self.DimSize[axis]=len(self.dim[dim_key])
        
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
    
    