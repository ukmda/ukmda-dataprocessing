# Copyright (C) 2018-2023 Mark McIntyre

# curateCamera.py
#
# python script to validate data before uploading to ukon live
#

import os
import sys
import fnmatch
import shutil
import glob

import configparser as cfg

from ufoutils import curateEngine as ce


def valid_date(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    if len(s) == 8:
        return True
    return False


def AddToRemoveList(fname, errf, movebad=False, msg='', nobjs=0, maxbri=0, tottotpx=0, useSubfolders=False, badfilepath='.'):
    _, fn = os.path.split(fname)
    namelen = len(fname)
    allf = fname[:namelen - 4] + '*'
    if movebad is True:
        print('moving file')
        bfp = badfilepath
        if useSubfolders is True:
            typ = msg.split(',')[0]
            bfp = os.path.join(badfilepath, typ)
            if os.path.exists(bfp) is False:
                os.mkdir(bfp)
        for fl in glob.glob(allf):
            _, fna = os.path.split(fl)
            trg = os.path.join(bfp, fna)
            if os.path.exists(trg):
                os.remove(trg)
            shutil.move(fl, trg)
    else:
        pass
    msg = msg + ',{:d},{:d}, {:d}'.format(nobjs, int(maxbri), int(tottotpx))
    print(fn + ',' + msg)
    if errf is not None:
        errf.write(fn + ',' + msg + '\n')


def ProcessADay(path, ymd, badfilepath, logfilepath, movebad, useSubfolders):
    try:
        listOfFiles = os.listdir(path)
    except:
        print('nothing to analyse')
        return
    listOfFiles.sort()
    pattern = 'M{:s}*P.jpg'.format(ymd)
    errf = open(os.path.join(logfilepath, 'results.txt'), 'a+')
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            x = entry.find('UK00')
            if x == -1:
                jpgname = os.path.join(path, entry)
                xmlname = jpgname[:len(jpgname) - 5] + ".xml"
                sts, msg, nobjs, maxbri, gtp, tottotpx = ce.CheckifValidMeteor(xmlname)
                if sts is False:
                    AddToRemoveList(xmlname, errf, movebad, msg, nobjs, maxbri, tottotpx, useSubfolders, badfilepath)
                else:
                    msg = msg + ',{:d},{:d}, {:d}'.format(nobjs, int(maxbri), int(tottotpx))
                    _, fn = os.path.split(xmlname)
                    print(fn + "," + msg)
                    if errf is not None:
                        errf.write(fn + ',' + msg + '\n')
    errf.close()
    return


def main(infname, ymd):
    if valid_date(ymd) is True:
        config = cfg.ConfigParser()
        config.read(infname)
        srcpath = config['camera']['localfolder']
        badfilepath = config['cleaning']['badfolder']
        logfilepath = badfilepath
        ce.logname = 'Curator: '
        ce.MAXRMS = float(config['cleaning']['maxrms'])
        ce.MINLEN = int(config['cleaning']['minlen'])
        ce.MAXLEN = int(config['cleaning']['maxlen'])
        ce.MAXBRI = int(config['cleaning']['maxbri'])
        ce.MAXOBJS = int(config['cleaning']['maxobjs'])

        if config['cleaning']['debug'] in ['True', 'TRUE', 'true']:
            ce.debug = True
        else:
            ce.debug = False
        movebad = False
        if config['cleaning']['movefiles'] in ['True', 'TRUE', 'true']:
            movebad = True
        useSubfolders = False
        if config['cleaning']['useSubfolders'] in ['True', 'TRUE', 'true']:
            useSubfolders = True  # noqa: F841

        yyyy = ymd[:4]
        yymm = ymd[:6]
        path = os.path.join(srcpath, yyyy, yymm, ymd)
        try:
            os.mkdir(badfilepath)
        except:
            pass
        try:
            os.mkdir(logfilepath)
        except:
            pass
        print('Processing ' + ymd + '; movefiles=' + str(movebad))
        ProcessADay(path, ymd, badfilepath, logfilepath, movebad, useSubfolders)
    else:
        print('Invalid date, must be YYYYMMDD')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('\nusage: python curateCamera.py camera_name yyyymmdd')
        print('eg python curateCamera.py tackley_tc 20200712')
        print('Reads config from an inifile -read example inifile for more info\n')
    else:
        # args should be id yyyymmdd
        infname = sys.argv[1]
        ymd = sys.argv[2]
        main(infname, ymd)
