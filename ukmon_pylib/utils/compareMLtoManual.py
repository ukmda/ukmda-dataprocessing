# compare ML and manual data to find differences, grab the relevant JPGs and flag them

import argparse
from RMS.Formats import FTPdetectinfo
from RMS.MLFilter import filterFTPdetectinfo
import os
import shutil


def processFolder(dir_path, threshold):
    dir_path = os.path.normpath(dir_path)

    ftp_name = 'FTPdetectinfo_' + os.path.split(dir_path)[1] + '.txt'

    filterFTPdetectinfo(os.path.join(dir_path, ftp_name), ML_threshold=threshold)

    if not os.path.isfile(os.path.join(dir_path, ftp_name)):
        print(f'Unable to open FTP file from {dir_path}')
        return 0
    conf_path = dir_path.replace('ArchivedFiles','ConfirmedFiles')
    if not os.path.isfile(os.path.join(conf_path, ftp_name)):
        print(f'Unable to open FTP file from {conf_path}')
        return 0

    _, _, manualFTP = FTPdetectinfo.readFTPdetectinfo(dir_path, ftp_name, True)
    _,_, autoFTP = FTPdetectinfo.readFTPdetectinfo(conf_path, ftp_name, True)

    manFFs=[]
    for ff in manualFTP:
        manFFs.append(ff[0])
    manFFs = list(set(manFFs))

    autoFFs=[]
    for ff in autoFTP:
        autoFFs.append(ff[0])
    autoFFs = list(set(autoFFs))

    #print(len(manFFs), len(autoFFs))
    #print(manFFs)
    #print(autoFFs)

    inManNotInAuto = list(set(manFFs).difference(autoFFs))
    inAutoNotInMan = list(set(autoFFs).difference(manFFs))

    print(f'selected manually but not by ML {inManNotInAuto}')
    print(f'selected by ML but not manually {inAutoNotInMan}')
    if len(inManNotInAuto) > 0 or len(inAutoNotInMan) > 0: 
        out_dir = dir_path.replace('ArchivedFiles','MLChecks')
        os.makedirs(out_dir, exist_ok=True)

        for ff in inManNotInAuto:
            srcfile = os.path.join(dir_path, ff.replace('.fits','.jpg'))
            targfile = os.path.join(out_dir, ff.replace('.fits','_man.jpg'))
            shutil.copy2(srcfile, targfile)
        for ff in inAutoNotInMan:
            srcfile = os.path.join(dir_path, ff.replace('.fits','.jpg'))
            targfile = os.path.join(out_dir, ff.replace('.fits','_auto.jpg'))
            shutil.copy2(srcfile, targfile)
    return


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description="Reads and filters meteors from FTPdetectInfo file.")
    arg_parser.add_argument('dir_path', nargs=1, metavar='dir_path', type=str,
        help='Path to the ArchivedFiles folder.')

    arg_parser.add_argument('-t', '--threshold', metavar='THR', type=float,
        help='Minimum threshold for acceptance.')

    cml_args = arg_parser.parse_args()
    threshold = 0.95
    if cml_args.threshold is not None:
        threshold=float(cml_args.threshold)

    dir_path = cml_args.dir_path[0]
    processFolder(dir_path, threshold)
