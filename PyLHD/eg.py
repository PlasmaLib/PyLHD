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

>>> data[key]

can be used.

Updated on Dec 12, 2016.
xarray support. Some methods are decided to be deprecated.
For the details, see http://xarray.pydata.org/

Updated on Oct 3, 2016
Created on Mar 28, 2016

@author: keisukefujii
'''

import numpy as np
import collections
import warnings
from copy import deepcopy
from datetime import datetime
import pandas as pd
import xarray as xr

def load(filename):
    """
    Load eg-file and returns as xarray.DataSet.

    To load the data from a file,

    >>>  array = eg.load(filename)
    """
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
    # xr.DataSet that will be created by this method.
    result = EGdata()
    # storing and reshape dims (dict)
    coords = collections.OrderedDict()
    for i in range(len(parameters['DimName'])):
        d = tmpdata[:,i].reshape(parameters['DimSize'])
        coords[parameters['DimName'][i]] = np.swapaxes(d, 0, i).flatten(order='F')[:parameters['DimSize'][i]]

    for i in range(len(parameters['ValName'])):
        result[parameters['ValName'][i]] = xr.DataArray(
                data = tmpdata[:,i+len(parameters['DimName'])].reshape(parameters['DimSize']),
                coords = coords,
                name = parameters['ValName'][i],
                attrs = {'Unit': parameters['ValUnit'][i]}
                )
    for key, item in parameters.items():
        result.attrs[key] = item
    result.attrs['comments'] = comments
    return result


def dump(dataset, filename, fmt='%.6e'):
    """
    Save xarray.Dataset to file.

    parameters:
    - dataset: xarray.Dataset object.
        To make the file compatibile to eg file, the following attributes are necessary.
        need_keys = ['NAME', 'DimUnit', 'ValUnit', 'ShotNo']
        To add these attributes to xarray.Dataset, call
        >>> dataset.attrs['NAME'] = 'some_name'
    - filename: path to file
    - fmt: format of the values. Same to np.savetxt. See
        https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html
        for the detail.
    """
    obj = dataset.copy(deep=True)
    # Make sure some necessary parameters are certainly stored
    need_keys = ['NAME', 'DimUnit', 'ValUnit',
                'ShotNo', 'DimSize']
    for need_key in need_keys:
        if need_key not in obj.attrs.keys():
            raise ValueError('There is no '+ need_key + ' property in ' + filename)

    # add some attributes
    obj.attrs['DimName'] = list(obj.coords.keys())
    obj.attrs['DimNo']   = len(obj.coords.keys())
    obj.attrs['DimSize'] = [len(item) for key, item in obj.coords.items()]
    obj.attrs['ValName'] = list(obj.data_vars.keys())
    obj.attrs['ValNo']   = len(obj.data_vars.keys())
    obj.attrs['Date']    = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

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
    # main parameters
    header = "[Parameters]\n"
    for key in ['NAME', 'ShotNo', 'Date', 'DimNo', 'DimName', 'DimSize',
                'ValNo', 'ValName', 'ValUnit']:
        item = obj.attrs[key]
        if isinstance(item, list):
            header += key + " = " + _list_to_strings(item) +"\n"
        else:
            header += key + " = " + str(item) +"\n"
        del obj.attrs[key] # remove already written entries.

    # other parameters
    for key, item in obj.attrs.items():
        if key is not 'comments':
            header += key + " = " + str(item) +"\n"

    # comments
    header += "\n[comments]\n"
    for key, item in obj.attrs['comments'].items():
        if isinstance(item, list):
            item = _list_to_strings(item)
        header += key + " = " + str(item) +"\n"
    # data start
    header += "\n[data]"

    #---  prepare 2d data to write into file ---
    data = []
    dimsize = [len(item) for key, item in obj.coords.items()]
    # prepare coords.
    for i, key, item in zip(list(range(len(obj.coords.keys()))),
                            obj.coords.keys(), obj.coords.values()):
        # expand dims to match the data_vars shape
        coord = item
        for j in range(len(obj.coords.keys())):
            if i != j:
                coord = np.expand_dims(coord, axis=j)
        # tile the expanded dims
        shape = deepcopy(dimsize)
        shape[i] = 1
        data.append(np.tile(coord, shape).flatten(order='C'))
    # append data_vars
    for key, item in obj.data_vars.items():
        data.append(item.values.flatten(order='C'))

    # write to file
    np.savetxt(filename, np.stack(data, axis=0).transpose(), header=header, delimiter=',', fmt=fmt)


class EGdata(xr.Dataset):
    """
    Object that stores eg-data.
    This methods inherites from xr.Dataset.

    Coordinate data is stored as OrderedDict
    >>> eg_data.coords

    To see what coordinates is stored,
    >>> eg_data.coords.keys()

    To access the particular coordinate, e.g. TIME,
    >>> eg_data.coords['TIME']
    or simply
    >>> eg_data['TIME']

    To see what values are stored,
    >>> eg_data.keys()
    which returns the list of names including coordinates.

    To access the data,
    >>> eg_data['... a key of the value']

    Full list of methods can be found in
    http://xarray.pydata.org/en/stable/api.html#dataarray
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
