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
from datetime import datetime


def load(filename):
    """
    Load metho to set eg-file into the memory.

    To load the data from a file,

    >>>  eg_data = eg.load(filename)

    The eg_data is EGdata object that has several parameters, dims, vals.
    See docs for EGdata.
    """
    eg_data = EGdata()
    # load [Parameters] and [comments] section
    eg_data._load_parameter_comments(filename)
    # load [data] section
    eg_data._load_data(filename)
    return eg_data

class EGdata(object):
    """
    Object that stores eg-data.
    Main parameters, NAME, ShotNo, SubShotNo, DimName, DimUnit, ValName, ValUnit
    is stored in self.NAME, self.ShotNo, ... etc.
    The dimension and values are stored in self.dim and self.val, respectively,
    both of which is OrderedDict.

    To see what is stored in this object, call

    >>> eg_data.dim.keys()
    >>> eg_data.val.keys()

    The dims and values can be accessed by

    >>> eg_data.dim[key]
    >>> eg_data.val[key]

    Each dim is 1d-np.array with size self.DimSizes[i], while all the val is
    (self.DimNo)d-np.array with shape self.DimSizes.
    """
    def __init__(self,
                NAME=None, ShotNo=None, SubShotNO=1, Date=None,
                DimName=None, DimUnit=None, ValName=None, ValUnit=None,
                *kw):
        """
        Initialize the eg-object.
        To register the analyzed-data-server,
        the following properties are necessary.
        NAME, ShotNo, SubShotNO, Date, DimNo, DimName, DimSize, DimUnit, ValNo,
        ValName, ValUnit

        Date, DimNo, DimSize, ValNo are set automatically at the output.
        """
        self.NAME = NAME
        self.ShotNo, self.SubShotNO = ShotNo, SubShotNO
        self.DimName, self.DimUnit = DimName, DimUnit
        self.ValName, self.ValUnit = ValName, ValUnit
        self.Date = None
        self.val = None
        self.dim = None

    def dump(self, filename):
        raise NotImplementedError
        """
        Save eg-file to memory.
        """
        # Make sure all the necessary parameters are assigned.
        assert(self.ShotNo is not None)
        assert(self.DimName is not None)
        assert(self.DimUnit is not None and len(self.DimUnit) == len(self.DimName))
        assert(self.ValName is not None)
        assert(self.ValUnit is not None and len(self.ValUnit) == len(self.ValName))
        if self.Date is None:
            self.Date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        # main parameters
        header = \
        "# [Parameters]\n"+\
        "# NAME = \'" + self.NAME + "\'\n" +\
        "# ShotNo = " + str(self.ShotNo) + "\n" +\
        "# Date = \'" + str(self.Date) + "\'\n" +\
        "# DimNo = "  + str(len(self.DimName)) + "\n" +\
        "# DimName = " + self._list_to_strings(self.DimName) + "\n" +\
        "# DimUnit = " + self._list_to_strings(self.DimUnit) + "\n" +\
        "# ValNo = "  + str(len(self.ValName)) + "\n"+\
        "# ValName = " + self._list_to_strings(self.ValName) + "\n" +\
        "# ValUnit = " + self._list_to_strings(self.ValUnit) + "\n#\n"
        # other parameters
        for key, item in self.parameters.items():
            header += "# " + key + " = " + str(item) +"\n"
        # comments
        header += "#\n# [comments] \n"
        for key, item in self.comments.items():
            header += "# " + key + " = " + str(item) +"\n"
        header += "# [data]"
        # write the data into file
        # TODO
        np.savetxt(filename, np.ones(1), header=header,
                    comments='', delimiter=',')


    def _list_to_strings(self, slist):
        # convert from list_of_strings to string
        string = ""
        for i in range(len(slist)-1):
            string += "\'"+slist[i] + "\',"
        string += "\'" + slist[-1] + "\'"
        return string

    # ["""# """ + key + """ = """ + item + """\n""" for key, item in self.parameters.items()] +
    # ["""# """ + key + """ = """ + item + """\n""" for key, item in self.comments.items()] +

    def __getitem__(self, index):
        """
        Return the slice of the data.
        """
        # TODO
        raise NotImplementedError

    def _load_parameter_comments(self, filename):
        """
        Load [Parameters] and [comments] parts of the eg-file.
        Main parameters are stored into self.__dict__, while the other ones are
        stored in self.parameters.
        All the comments are stored into self.comments.
        """
        self.parameters = collections.OrderedDict()
        self.comments = collections.OrderedDict()
        # load [Parameters] and [Comments] section
        f = open(filename, 'r')
        for line in f:
            if '# [Parameters]'.lower() in line.lower():
                block = 'Parameters'
            elif '# [comments]'.lower() in line.lower():
                block = 'comments'
            elif '# [data]'.lower() in line.lower():
                break # data is read np.loadtxt
            elif not '#' in line:
                break # Finish reading.
            # read Parameters block
            elif block is 'Parameters':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip().lower()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                # string
                if key == 'NAME'.lower():
                    self.NAME = val
                # list of string
                elif key == 'DimName'.lower():
                    self.DimName = val.split(',')
                elif key == 'DimUnit'.lower():
                    self.DimUnit = val.split(',')
                elif key == 'ValName'.lower():
                    self.ValName = val.split(',')
                elif key == 'ValUnit'.lower():
                    self.ValUnit = val.split(',')
                # string
                elif key == 'Date'.lower():
                    self.Date = val
                # integers
                elif key == 'DimNo'.lower():
                    self.DimNo = int(val)
                elif key == 'ValNo'.lower():
                    self.ValNo = int(val)
                elif key == 'ShotNo'.lower():
                    self.ShotNo = int(val)
                elif key == 'SubShotNO'.lower():
                    self.SubShotNO = int(val)
                # list of integers
                elif key == 'DimSize'.lower():
                    self.DimSize = [int(s) for s in val.split(',')]
                else: # the rest of parameters
                    if key is not None and len(key)>0:
                        self.parameters[key] = line[line.find('=')+1:].strip()
            # read Comments block
            elif block is 'comments':
                key = line[line.find('#')+1:line.find("=")].strip()
                if key is not None:
                    self.comments[key] = line[line.find('=')+1:].strip()
        # Remember to close file
        f.close()

    def _load_data(self, filename):
        # temporary data
        tmpdata = np.loadtxt(filename, comments='#', delimiter=',')
        # preparing dict
        self.dim = collections.OrderedDict()
        self.val = collections.OrderedDict()
        # storing and reshape dims (dict)
        for i in range(len(self.DimName)):
            d = tmpdata[:,i].reshape(self.DimSize)
            self.dim[self.DimName[i]] = np.swapaxes(d, 0, i).flatten(order='F')[:self.DimSize[i]]
        # storing and reshape vals (dict)
        for i in range(len(self.ValName)):
            self.val[self.ValName[i]] = tmpdata[:,i+len(self.DimName)].reshape(self.DimSize)


    def _slice(self, index, axis=0):
        """
        Crop the original data and through away the rest.
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
