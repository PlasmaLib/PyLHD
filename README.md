# PyLHD
[ ![Codeship Status for PlasmaLib/PyLHD](https://app.codeship.com/projects/ab440c70-e2f5-0134-5e64-366de5b2fd76/status?branch=master_public)](https://app.codeship.com/projects/205937)
[![codecov](https://codecov.io/gh/PlasmaLib/PyLHD/branch/master_public/graph/badge.svg)](https://codecov.io/gh/PlasmaLib/PyLHD)


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
