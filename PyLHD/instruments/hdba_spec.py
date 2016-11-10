"""
Methods to read the binary file for HDBA-spec
"""

import numpy as np
from six.moves import configparser
import os
import csv
import collections
from collections import OrderedDict

CONFIG_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__))) + '/hdba_spec/'
CONFIG_LIST_FILE = CONFIG_DIR + 'config_list.txt'

def load(data_filename, prm_filename, shotnumber):
    """
    Load binary file from 'filename'
    """
    config = Config()
    config.read(shotnumber)
    return HDBASpec(data_filename, prm_filename, config)


class Config(object):
    """
    This object have config object for the HDBASpec.
    """
    def __init__(self):
        self.config_list = []
        with open(CONFIG_LIST_FILE, 'r') as f:
            reader = csv.reader(f, )
            for row in reader:
                if row[0][0] != '#':
                    # shotnumber
                    self.config_list.append({
                        'start_shot': int(row[0]),
                        'setting_file':   row[1].replace(" ", ""),
                        'calib_file':     row[2].replace(" ", ""),
                        'wavelength_file':row[3].replace(" ", "")
                    })

    def _find_config_files(self, shotnumber):
        """
        This method returns dictionary object that is used for the experiment.
        """
        # raise an error if there is no config file
        if shotnumber < self.config_list[0]['start_shot']:
            raise ValueError('There is no config file for shot '+ str(shotnumber))
        for i in range(1+len(self.config_list)):
            if self.config_list[i-1]['start_shot'] <= shotnumber and \
               self.config_list[i  ]['start_shot'] > shotnumber:
                return self.config_list[i-1]
            else:
                return self.config_list[-1]

    def read(self, shotnumber):
        """
        Find and read config file.
        """
        # find config file
        config_files = self._find_config_files(shotnumber)
        self.setting_file    = config_files['setting_file']
        self.wavelength_file = config_files['wavelength_file']
        self.calib_file      = config_files['calib_file']
        # read parameter files
        self.wavelength = self._reader(CONFIG_DIR+self.wavelength_file)
        self.calib      = self._reader(CONFIG_DIR+self.calib_file)
        self.settings   = self._settting_reader(CONFIG_DIR+self.setting_file)

    def _reader(self, filename):
        """
        This method distinguish IGOR itx file or usual textfile
        and read its contents.
        """
        with open(filename, 'r') as f:
            if 'IGOR' in f.readline():
                # IGOR itx file
                return np.loadtxt(filename, delimiter=",", skiprows=3)
            else:
                # simple csv file
                return np.loadtxt(filename, delimiter="\t", skiprows=1)

    def _settting_reader(self, filename):
        """
        This method reads config files and covnerts to dict.
        """
        parser = configparser.ConfigParser()
        if not os.path.exists(filename):
            raise IOError('There is no setting file: '+ filename)
        parser.read(filename)
        return namedtuplify(parser._sections)


class HDBASpec(object):
    def __init__(self, data_filename, prm_filename, config):
        """
        data_filename: absolute path for HDBASpec raw data
        prm_filename:  absolute path for HDBASpec prm data
        config: Config object
        """
        # Background_subtraction
        self._background_subtraction()
        # Reorder to fiber number
        self._reorder()
        # caibration
        self._calibrate()

    def _background_subtraction(self):
        """
        Estimate the background from the unused fiber image.
        """
        pass

    def _reorder(self):
        """
        Reorder fiber number to los.
        """
        pass

    def _calibrate(self):
        """
        Make a calibration.
        """
        pass

"""
Method related to config files
"""
# a very simple parser
def parse(string):
    if type(string) is not str:
        raise ValueError
    if string in ['true', 'True']:
        return True
    elif string in ['false', 'False']:
        return False
    elif any([string.count(s) for s in ',']): #likely list
        slist = string.split(',')
        return [parse(s) for s in slist] # execute recursively
    elif any([string.count(s) for s in '.eE']):
        try:
            return float(string)
        except:
            return string
    else:
        try:
            return int(string)
        except:
            return string

# make the dictionary into a nested series of named tuples. This is what allows
# accessing by attribute: settings.numerics.jitter
def namedtuplify(mapping):  # thank you https://gist.github.com/hangtwenty/5960435
    if isinstance(mapping, collections.Mapping):
        for key, value in list(mapping.items()):
            mapping[key] = namedtuplify(value)
        try:
            mapping.pop('__name__')
        except:
            pass
        # return collections.namedtuple('settingsa', dict(**mapping))(**mapping)
        return MutableNamedTuple(mapping)
    return parse(mapping)

class MutableNamedTuple(OrderedDict):
    """
    A class that doubles as a mutable named tuple, to allow settings to be re-set during
    """
    def __init__(self, *args, **kwargs):
        super(MutableNamedTuple, self).__init__(*args, **kwargs)
        self._settings_stack = []
        self._initialised = True

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if not hasattr(self, "_initialised"):
            super(MutableNamedTuple, self).__setattr__(name, value)
        else:
            super(MutableNamedTuple, self).__setitem__(name, value)
