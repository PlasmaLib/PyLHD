# PyLHD
[ ![Codeship Status for PlasmaLib/PyLHD](https://app.codeship.com/projects/a765be20-b523-0134-c68d-5ed8b845772e/status?branch=master)](https://app.codeship.com/projects/193957)
[![codecov](https://codecov.io/gh/PlasmaLib/PyLHD/branch/master/graph/badge.svg?token=dnDhzru5u7)](https://codecov.io/gh/PlasmaLib/PyLHD)


Python library for the LHD experiments.

This library includes several components.

Currently, we mainly support input/output scripts that can handle LHD experiment data.

## Input/Output
+ eg: Module that read and write eg data format that is used as *analyzed-data*.  
This module is built on top of [**xarray**](http://xarray.pydata.org/),
which brings N-dimensional variants of the core pandas data structures.  
The basic usage can be found in this [**notebook**](notebooks/eg.ipynb).

+ igetfile: Module that download the analyzed data files from *analyzed data server*.  
This module generates eg data file,
so that the above *eg* module can be used for the downloaded file.  
The basic usage can be found in this [**notebook**](notebooks/igetfile.ipynb).
Note that this only works in the NIFS-experiment-network.

+ PVwave: Read PVwave binary file from Python.

To use the above files, please contact us.
