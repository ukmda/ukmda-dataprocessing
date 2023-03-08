# Copyright (C) 2018-2023 Mark McIntyre

# compare ML and manual data to find differences, grab the relevant JPGs and flag them

import argparse
from RMS.Formats import FTPdetectinfo
from RMS.MLFilter import filterFTPdetectinfoML
import RMS.ConfigReader as cr
import os
import shutil
import glob
import json


def summariseAMonth(dir_path, currmth):
    camlist = {'UK0006','UK000F','UK001L','UK002F'}
    print('cam, month, total, falseneg, falsepos')
    for cam in camlist:            
        dir_path = os.path.normpath(dir_path)
        base_path = os.path.join(dir_path, cam, 'MLChecks')
        mldb = os.path.join(base_path, 'mlcheck.json')
        dbjson = json.load(open(mldb, 'r'))
        keys=[d for d in dbjson if d.startswith(currmth)]
        tmpjs = {}
        for k in keys:
            tmpjs[k] = dbjson[k]
        total=sum([d['total'] for d in tmpjs.values()])
        totneg=sum([d['falseneg'] for d in tmpjs.values()])
        totpos=sum([d['falsepos'] for d in tmpjs.values()])
        print(f'{cam}, {currmth}, {total}, {totneg}, {totpos}')
    return


def writeDB(dir_path, results):
    dir_path = os.path.normpath(dir_path)
    base_path = os.path.join(os.path.split(os.path.split(dir_path)[0])[0], 'MLChecks')
    currdt = os.path.split(dir_path)[1]
    currdt = currdt[7:15]
    mldb = os.path.join(base_path, 'mlcheck.json')
    if os.path.isfile(mldb):
        dbjson = json.load(open(mldb, 'r'))
    else:
        dbjson = {}
    dbjson[currdt] = results
    json.dump(dbjson, open(mldb, 'w'), indent=2)
    return 


def processFolder(dir_path, threshold, kpng):
    dir_path = os.path.normpath(dir_path)

    ftp_name = 'FTPdetectinfo_' + os.path.split(dir_path)[1] + '.txt'

    config = cr.loadConfigFromDirectory('.config', dir_path)

    filterFTPdetectinfoML(config, os.path.join(dir_path, ftp_name), threshold=threshold, keep_pngs=kpng)

    if not os.path.isfile(os.path.join(dir_path, ftp_name)):
        print(f'Unable to open FTP file from {dir_path}')
        return {'total': 0, 'falseneg': 0, 'falsepos': 0}
    conf_path = dir_path.replace('ArchivedFiles','ConfirmedFiles')
    if not os.path.isfile(os.path.join(conf_path, ftp_name)):
        print(f'Unable to open FTP file from {conf_path}')
        return {'total': 0, 'falseneg': 0, 'falsepos': 0}

    # auto FTP is the one in ArchivedFiles
    _, _, autoFTP = FTPdetectinfo.readFTPdetectinfo(dir_path, ftp_name, True)
    _,_, manualFTP = FTPdetectinfo.readFTPdetectinfo(conf_path, ftp_name, True)

    manFFs=[]
    for ff in manualFTP:
        manFFs.append(ff[0])
    manFFs = list(set(manFFs))

    autoFFs=[]
    for ff in autoFTP:
        autoFFs.append(ff[0])
    autoFFs = list(set(autoFFs))

    inManNotInAuto = list(set(manFFs).difference(autoFFs))
    inAutoNotInMan = list(set(autoFFs).difference(manFFs))

    totaldets = len(autoFFs)
    falsenegs = len(inManNotInAuto)
    falseposs = len(inAutoNotInMan)

    results = {'total': totaldets, 'falseneg': falsenegs, 'falsepos': falseposs}

    print(f'rejected by ML {inManNotInAuto}')
    print(f'selected by ML {inAutoNotInMan}')
    if len(inManNotInAuto) > 0 or len(inAutoNotInMan) > 0: 
        out_dir = dir_path.replace('ArchivedFiles','MLChecks')
        out_dir = os.path.split(out_dir)[0]
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(os.path.join(out_dir,'falsepos'), exist_ok=True)
        os.makedirs(os.path.join(out_dir,'falseneg'), exist_ok=True)

        for ff in inManNotInAuto:
            srcfile = os.path.join(dir_path, ff.replace('.fits','.jpg'))
            targfile = os.path.join(out_dir, 'falseneg', ff.replace('.fits','_artefact.jpg'))
            shutil.copy2(srcfile, targfile)
            if os.path.exists(os.path.join(dir_path, 'temp_png_dir','artefacts')):
                flist = glob.glob(os.path.join(dir_path, 'temp_png_dir','artefacts', ff.replace('.fits','*.png')))
                for fl in flist:
                    _, fname = os.path.split(fl)
                    targfile = os.path.join(out_dir, 'falseneg', fname)
                    shutil.copy2(fl, targfile)
        for ff in inAutoNotInMan:
            srcfile = os.path.join(dir_path, ff.replace('.fits','.jpg'))
            targfile = os.path.join(out_dir, 'falsepos', ff.replace('.fits','_meteor.jpg'))
            shutil.copy2(srcfile, targfile)
            if os.path.exists(os.path.join(dir_path, 'temp_png_dir','meteors')):
                flist = glob.glob(os.path.join(dir_path, 'temp_png_dir','meteors', ff.replace('.fits','*.png')))
                for fl in flist:
                    _, fname = os.path.split(fl)
                    targfile = os.path.join(out_dir, 'falsepos', fname)
                    shutil.copy2(fl, targfile)
    return results


def filterResults(fname):
    with open(fname, 'r') as inf:
        lis = inf.readlines()
    tots = 0
    excl = 0
    false_pos = []
    false_neg = []
    for li in lis:
        if 'modified' in li and 'records as artefacts' in li:
            spls = li.split(' ')
            counts = spls[6]
            ex, tot = counts.split('/')
            excl += int(ex)
            tots += int(tot)
        if 'rejected by ML' in li:
            ffs = li.strip().split('[')[1][:-1].split(',')
            if len(ffs[0]) > 5:
                for ff in ffs:
                    false_neg.append(ff.strip())
        if 'selected by ML' in li:
            ffs = li.strip().split('[')[1][:-1].split(',')
            if len(ffs[0]) > 5:
                for ff in ffs:
                    false_pos.append(ff.strip())
    false_pos.sort()
    false_neg.sort()
    with open(fname[:-4]+'_filtered.log', 'w') as outf:
        outf.write(f'total processed {tots}, total removed {excl}\n')
        outf.write(f'false pos: {len(false_pos)}, false neg: {len(false_neg)}\n')
        outf.write('Included by ML but visually excluded\n')
        for ff in false_pos:
            outf.write(f'{ff}\n')
        outf.write('Excluded by ML but visually included\n')
        for ff in false_neg:
            outf.write(f'{ff}\n')
    return 


def getScores(fname):
    with open(fname, 'r') as inf:
        lis = inf.readlines()
    results = []
    for li in lis:
        if 'identified as' in li:
            ff, score, _, _, _ = li.replace('  ', ' ').strip().split(' ')
            score = float(score[:-1])
            results.append({'ff': ff, 'score': score})
    results.sort(key=lambda s: s['score'])
    return results


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description="Reads and filters meteors from FTPdetectInfo file.")
    arg_parser.add_argument('dir_path', nargs=1, metavar='dir_path', type=str,
        help='Path to the ArchivedFiles folder.')
    arg_parser.add_argument('-t', '--threshold', metavar='THR', type=float,
        help='Minimum threshold for acceptance.')
    arg_parser.add_argument('--keep_pngs', '-p', metavar='KEEPPNGS', type=int,
        help='keep pngs (1) or delete them (0)')

    cml_args = arg_parser.parse_args()
    threshold = 0.95
    if cml_args.threshold is not None:
        threshold=float(cml_args.threshold)

    kpng = 1
    if cml_args.keep_pngs is not None:
        kpng = cml_args.keep_pngs

    dir_path = cml_args.dir_path[0]
    results = processFolder(dir_path, threshold, kpng)

    writeDB(dir_path, results)
