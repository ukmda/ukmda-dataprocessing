#
# Create additional information from pickled Trajectory file
#
import os
import sys
import glob
import csv
import shutil

import boto3

from wmpl.Trajectory.Trajectory import Trajectory
from wmpl.Utils.Pickling import loadPickle 
from wmpl.Utils.TrajConversions import jd2Date
from datetime import datetime, timedelta

from ufoTrajSolver import createAdditionalOutput


def getCameraDetails():
    # fetch camera details from the CSV file
    fldrs = []
    cams = []
    lati = []
    alti = []
    longi = []
    camtyp = []
    fullcams = []
    dummyid = []
    camfile = 'camera-details.csv'

    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + camfile, camfile)
    with open(camfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0][:1] != '#':
                if row[1] == '':
                    fldrs.append(row[0])
                else:
                    fldrs.append(row[0] + '/' + row[1])
                if int(row[11]) == 1:
                    cams.append(row[2] + '_' + row[3])
                else:
                    cams.append(row[2])
                fullcams.append(row[0] + '_' + row[3])
                longi.append(float(row[8]))
                lati.append(float(row[9]))
                alti.append(float(row[10]))
                camtyp.append(int(row[11]))
                dummyid.append(row[12])
    os.remove(camfile)
    return cams, fldrs, lati, longi, alti, camtyp, fullcams, dummyid


def generateExtraFiles(outdir):

    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    traj.save_results = True

    createAdditionalOutput(traj, outdir)
    fetchJpgsAndMp4s(traj, outdir)
    return


def fetchJpgsAndMp4s(traj, outdir):
    archdir = os.getenv('ARCHDIR')
    if len(archdir) < 5:
        archdir='/home/ec2-user/ukmon-shared/archive'

    print('getting camera details file')
    _, fldrs, _, _, _, _, _, dummyid = getCameraDetails()
    for obs in traj.observations:
        statid = obs.station_id
        ci = dummyid.index(statid)
        fldr = fldrs[ci]
        print(statid, fldr)
        evtdate = jd2Date(obs.jdt_ref, dt_obj=True)

        print('station {} event {} '.format(statid, evtdate.strftime('%Y%m%d-%H%M%S')))
        # if the event is after midnight the folder will have the previous days date
        if evtdate.hour < 12:
            evtdate += timedelta(days=-1)
        yr = evtdate.year
        ym = evtdate.year * 100 + evtdate.month
        ymd = ym *100 + evtdate.day

        print('getting jpgs and mp4s')
        thispth = '{:s}/{:04d}/{:06d}/{:08d}/'.format(fldr, yr, ym, ymd)
        srcpath = os.path.join(archdir, thispth)
        print(thispth)
        flist = glob.glob1(srcpath, 'FF*.jpg')
        srcfil = None
        for fil in flist:
            spls = fil.split('_')
            fdt = datetime.strptime(spls[2] + '_' + spls[3],'%Y%m%d_%H%M%S')
            tdiff = (evtdate - fdt).seconds
            if tdiff > 0 and tdiff < 11:
                srcfil = fil
                break
        if srcfil is not None:
            srcfil = srcpath + srcfil
            shutil.copy2(srcfil, outdir)
            file_name, _ = os.path.splitext(srcfil)
            srcfil = file_name + '.mp4'
            try:
                shutil.copy2(srcfil, outdir)
            except FileNotFoundError:
                pass
        else:
            print('no jpgs in {}'.format(srcpath))

        print('R90 CSV, KML and FTPDetect file')
        flist = os.listdir(srcpath)
        for fil in flist:
            file_name, file_ext = os.path.splitext(fil)
            if ('FTPdetectinfo' in fil) and (file_ext == '.txt') and ('_original' not in file_name) and ('_uncal' not in file_name) and ('_backup' not in file_name):
                srcfil = srcpath + fil
                shutil.copy2(srcfil, outdir)
            elif file_ext == '.csv':
                srcfil = srcpath + fil
                shutil.copy2(srcfil, outdir)
            elif file_ext == '.kml':
                srcfil = srcpath + fil
                shutil.copy2(srcfil, outdir)
                kmldir = os.path.join(archdir, 'kmls')
                shutil.copy2(srcfil, kmldir)

    return


if __name__ == '__main__':
    generateExtraFiles(sys.argv[1])
