# PyLHD
Python library for the LHD experiments.

This library includes several components.

## Input/Output
+ retrieve: Download raw data files from raw data server.
+ igetfile: Download analyzed data files from analyzed data server.
+ PVwave: Read PVwave binary file from Python.

### Note

Currently, we are not allowed to publish the following files,
+ `igetfile` : executable to download the eg-data
+ `igetfile.py` : Python script to execute `igetfile`
+ `retrieve` : executable to download the raw data
+ `retrieve_t` : executable to download the timing data

To use the above files, please contact us.
