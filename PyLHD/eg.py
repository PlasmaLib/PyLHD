'''
A function that reads eg file for the LHD experiment.
The typical usage is

>>> data = eg.load(filename)

The dimension axis is stored in self.dim (ordered dict), while the data are
stored self.val (ordered dict)

To check the contents,

>>> data.dim.keys()

>>> data.val.keys()

To access the data,

>>> data.dim[key]

>>> data.val[key]

can be used.

Created on Mar 28, 2016
Updated on Oct 3, 2016

@author: keisukefujii
'''

import numpy as np
import collections
import warnings
from datetime import datetime
import xarray as xr

def load(filename):
    """
    Load eg-file and returns as xarray.DataSet.

    To load the data from a file,

    >>>  array = eg.load(filename)
    """
    # xr.DataSet that will be created by this method.
    result = EGdata()
    """
    First, we load [Parameters] and [comments] parts of the eg-file.
    Parameters are stored in xarray.DataArray.attrs as an OrderedDict.
    """
    parameters = collections.OrderedDict()
    comments = collections.OrderedDict()
    # load [Parameters] and [Comments] section
    with open(filename, 'r') as f:
        for line in f:
            if '[parameters]' in line.lower():
                block = 'Parameters'
            elif '[comments]' in line.lower():
                block = 'comments'
            elif '[data]' in line.lower():
                break # data is read np.loadtxt
            elif not '#' in line:
                break # Finish reading.
            # read Parameters block
            elif block is 'Parameters':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                # string
                if key.lower() == 'NAME'.lower():
                    parameters['NAME'] = val
                # list of string
                elif key.lower() == 'DimName'.lower():
                    parameters['DimName'] = val.split(',')
                elif key.lower() == 'DimUnit'.lower():
                    parameters['DimUnit'] = val.split(',')
                elif key.lower() == 'ValName'.lower():
                    parameters['ValName'] = val.split(',')
                elif key.lower() == 'ValUnit'.lower():
                    parameters['ValUnit'] = val.split(',')
                # string
                elif key.lower() == 'Date'.lower():
                    parameters['Date'] = val
                # integers
                elif key.lower() == 'DimNo'.lower():
                    parameters['DimNo'] = int(val)
                elif key.lower() == 'ValNo'.lower():
                    parameters['ValNo'] = int(val)
                elif key.lower() == 'ShotNo'.lower():
                    parameters['ShotNo'] = int(val)
                elif key.lower() == 'SubShotNO'.lower():
                    parameters['SubShotNO'] = int(val)
                # list of integers
                elif key.lower() == 'DimSize'.lower():
                    parameters['DimSize'] = [int(s) for s in val.split(',')]
                else: # the rest of parameters                # string
                    if key is not None and len(key)>0:
                        parameters[key] = line[line.find('=')+1:].strip()

            elif block is 'comments':
                # Make lower case
                key = line[line.find('#')+1:line.find("=")].strip()
                # remove '(quotation) and , (space)
                val = line[line.find('=')+1:].replace(" ","").replace("'", "").strip()
                if key is not None and len(key)>0:
                    comments[key] = line[line.find('=')+1:].strip()

        # Make sure some necessary parameters are certainly stored
        need_keys = ['NAME', 'DimName', 'DimUnit', 'ValName', 'ValUnit', 'Date',
                    'DimNo', 'ValNo', 'ShotNo', 'DimSize']
        for need_key in need_keys:
            if need_key not in parameters.keys():
                raise ValueError('There is no '+ need_key + ' property in ' + filename)
    """
    Next, we load [Data] part of file.
    """
    # temporary data
    tmpdata = np.loadtxt(filename, comments='#', delimiter=',')
    # preparing coordinates
    coords = []
    # storing and reshape dims (dict)
    for i in range(len(parameters['DimName'])):
        d = tmpdata[:,i].reshape(parameters['DimSize'])
        coords.append(np.swapaxes(d, 0, i).flatten(order='F')[:parameters['DimSize'][i]])

    for i in range(len(parameters['ValName'])):
        result[parameters['ValName'][i]] = xr.DataArray(
                data = tmpdata[:,i+len(parameters['DimName'])].reshape(parameters['DimSize']),
                coords = coords,
                dims = parameters['DimName'],
                attrs = {'Name': parameters['ValName'][i],
                         'Unit': parameters['ValUnit'][i]}
                )
    for key, item in parameters.items():
        result.attrs[key] = item
    result.attrs['comments'] = comments
    return result

class EGdata(xr.Dataset):
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
    @property
    def dim(self):
        warnings.warn('\'dim\' property is deprecated. Use \'coords\' or [] operator instead.',
                                            DeprecationWarning, stacklevel=2)
        return self.coords

    @property
    def val(self):
        warnings.warn('\'val\' property is deprecated. Use [] operator instead.',
                                            DeprecationWarning, stacklevel=2)
        return self.data_vars

    @property
    def comments(self):
        warnings.warn('\'comments\' property is deprecated. Access via self.atttrs[\'comments\'].',
                                            DeprecationWarning, stacklevel=2)
        return self.attrs['comments']

    def __getattribute__(self, key):
        """
        Overwrite __getattribute__ to keep the backcompatibility
        """
        o = object.__getattribute__(self, key)
        # Officially supported properties
        if key in ['NAME', 'ShotNo','DimNo', 'DimName', 'DimSize', 'DimUnit',
        'ValNo', 'ValName','ValUnit']:
            return self.attrs[key]
        return o

    def dump(self, filename):
        """
        Save eg-file to memory.
        """
        # Make sure some necessary parameters are certainly stored
        need_keys = ['NAME', 'DimName', 'DimUnit', 'ValName', 'ValUnit',
                    'DimNo', 'ValNo', 'ShotNo', 'DimSize']
        for need_key in need_keys:
            if need_key not in self.attrs.keys():
                raise ValueError('There is no '+ need_key + ' property in ' + filename)

#    if 'Date' not in self.attrs.keys():
        self.attrs['Date'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        # --- A simple method to convert list to string ----
        def _list_to_strings(slist):
            # convert from list_of_strings to string
            string = ""
            # a simple method to make string from string or integer
            def _str(s):
                return '\''+s+'\'' if isinstance(s, str) else str(s)

            for i in range(len(slist)-1):
                string += _str(slist[i])+', '
            string += _str(slist[-1])
            return string
        # ---- end of this method ---

        # prepare the header
        # parameters
        header = "# [Parameters]\n"
        for key, item in self.attrs.items():
            if key is not 'comments':
                if isinstance(item, list):
                    header += "# " + key + " = " + _list_to_strings(item) +"\n"
                else:
                    header += "# " + key + " = " + str(item) +"\n"
        # comments
        comments = "# [comments]\n"
        for key, item in self.attrs['comments'].items():
            if isinstance(item, list):
                item = _list_to_strings(item)
            header += "# " + key + " = " + str(item) +"\n"
        # data start
        header += "# [data]"

        # write the data into file
        # TODO Needs to complete. Script to reshape axis is nescessary.
        raise NotImplementedError()
        np.savetxt(filename, np.ones(1), header=header,
                    comments='', delimiter=',')
        return filename


    # ["""# """ + key + """ = """ + item + """\n""" for key, item in self.parameters.items()] +
    # ["""# """ + key + """ = """ + item + """\n""" for key, item in self.comments.items()] +
    '''
    def __getitem__(self, index):
        """
        Return the cropped data.
        :param index: The cropping indices. The data[index_start] will be kept.
        :param axis: The axis where the cropping should be applied.
        :return : The cloned eg_data
        """
        # for val
        cropped_data = EGdata(NAME=self.NAME, ShotNo=self.ShotNo,
                    SubShotNO=self.SubShotNO,
                    Date=self.Date, DimName=self.DimName, DimUnit=self.DimUnit,
                    ValName=self.ValName, ValUnit=self.ValUnit)
        # copy the comment
        cropped_data.parameters = self.parameters
        cropped_data.comments = self.comments
        # copy val
        cropped_data.val = collections.OrderedDict()
        for key, item in self.val.items():
            cropped_data.val[key] = item[index]
        # prepare dim
        cropped_data.dim = self.dim
        cropped_data.DimSize = self.DimSize
        dim_key = list(self.dim.keys())
        # 1-dim case
        if isinstance(index, (list, slice)) or len(index.shape) == 1:
            cropped_data.dim[dim_key[0]] = self.dim[dim_key[0]][index]
            cropped_data.DimSize[0]=len(cropped_data.dim[dim_key[0]])
        else:
            # TODO
            raise NotImplementedError
        # for DimSize
        return cropped_data
    '''

    def val_property(self):
        """
        Return ordered_dict that connects ValName and ValUnit
        """
        prop = collections.OrderedDict()
        for name, unit in zip(self.ValName, self.ValUnit):
            prop[name] = unit
        return prop

    def dim_property(self):
        """
        Return ordered_dict that connects DimName and DimUnit
        """
        prop = collections.OrderedDict()
        for name, unit in zip(self.DimName, self.DimUnit):
            prop[name] = unit
        return prop
