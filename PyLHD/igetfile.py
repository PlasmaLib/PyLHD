#!/usr/bin/env python
# coding: utf-8
'''
A function that downloads eg data from LHD server, which is provided by LHD
diagnostic team.

The typical usage is

>>> igetfile(diagname, shotenum, subshotnum, output_name)

Returns the output-filename.
To read the data, eg.loadtxt(output_filename)
can be used.
'''

from ftplib import FTP
import zipfile
import os
from optparse import OptionParser

def ftpGet(targetpath, outputpath):
    ftp = FTP('egftp1.lhd.nifs.ac.jp')
    ftp.login()
    cmd = 'RETR %s' % targetpath
    fpo = open(outputpath, 'wb')
    ftp.retrbinary(cmd, fpo.write)
    fpo.close()
    ftp.quit()

def ftpList(targetpath):
    ftp = FTP('egftp1.lhd.nifs.ac.jp')
    ftp.login()
    flist = ftp.nlst(targetpath)
    ftp.quit()
    return flist

def unzip(targetfile):
    zf = zipfile.ZipFile(targetfile, 'r')
    flist = []
    for target in zf.namelist():
        try:
            data = zf.read(target)
            fpo = open(target, 'wb')
            fpo.write(data)
            fpo.close()
            flist.append(target)
        except:
            data = None
    zf.close()
    os.remove(targetfile)
    return flist


def icheckfile(diagname, shotno, subshot):
    targetfolderpath = 'data/'
    targetfolderpath = targetfolderpath + diagname + '/'
    firstshotno = int(shotno / 1000) * 1000
    firstfolder = '%06d/' % firstshotno
    targetfolderpath = targetfolderpath + firstfolder
    secondfolder = '%06d/' % shotno
    targetfolderpath = targetfolderpath + secondfolder
    subfolder = '%06d' % subshot
    targetfolderpath = targetfolderpath + subfolder
    #print targetfolderpath
    filelist = ftpList(targetfolderpath)
    if 0 == len(filelist):
        return False
    return True

def igetfile(diagname, shotno, subshot, outputname):
    targetfolderpath = 'data/'
    targetfolderpath = targetfolderpath + diagname + '/'
    firstshotno = int(shotno / 1000) * 1000
    firstfolder = '%06d/' % firstshotno
    targetfolderpath = targetfolderpath + firstfolder
    secondfolder = '%06d/' % shotno
    targetfolderpath = targetfolderpath + secondfolder
    subfolder = '%06d' % subshot
    targetfolderpath = targetfolderpath + subfolder
    #print targetfolderpath
    filelist = ftpList(targetfolderpath)
    if 0 == len(filelist):
        return None
    for fn in filelist:
        if fn[-4:].upper() == '.ZIP':
            targetpath = fn
            targetfile = targetpath.split('/')[-1]
            print(targetpath) # support python 3
            print(targetfile)
            ftpGet(targetpath, targetfile)
            files = unzip(targetfile)
            os.rename(files[0], outputname)
    return outputname

if __name__ == '__main__':
    #fpath = 'data/lhdcxs7_cvi/103000/103912/000001/lhdcxs7_ti@103912.dat.zip'
    parser = OptionParser()
    parser.add_option("-s", "--shot", dest="shotno",
            help = "Shot number", metavar="SHOTNO")
    parser.add_option("-m", "--sub", dest="subshotno",
            help = "Subshot number", metavar="SUBSHOTNO")
    parser.add_option("-d", "--diagname", dest="diagname",
            help = "Diagnostic name", metavar="DIAGNAME")
    parser.add_option("-o", "--output", dest="output",
            help = "Output filename", metavar="OUTPUT")
    (options, args) = parser.parse_args()
    shotno = options.shotno
    subshotno = options.subshotno
    diagname = options.diagname
    output = options.output
    try:
        sn = int(shotno)
    except:
        exit(-1)
    try:
        sub = int(subshotno)
    except:
        exit(-1)
    if not diagname:
        exit(-1)
    if not output:
        exit(-1)

    ret = igetfile(diagname, sn, sub, output)
    if ret == None:
        print('Error: there is no data for the shot.')
        exit(-1)
    exit(0)
