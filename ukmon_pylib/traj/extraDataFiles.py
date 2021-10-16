#
# Create additional information from pickled Trajectory file
#
import os
import sys
import glob
import shutil

from wmpl.Utils.Pickling import loadPickle 
from wmpl.Utils.TrajConversions import jd2Date
from datetime import datetime, timedelta
from traj.ufoTrajSolver import createAdditionalOutput, calcAdditionalValues
import fileformats.CameraDetails as cdet


def generateExtraFiles(outdir):

    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    traj.save_results = True

    createAdditionalOutput(traj, outdir)
    findMatchingJpgs(traj, outdir)
    #fetchJpgsAndMp4s(traj, outdir)
    return


def getVMagCodeAndStations(outdir):

    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    amag, bestvmag, mass, id, cod, orb, shower_obj, lg, bg, vg, stations = calcAdditionalValues(traj)
    return bestvmag, cod, stations


def findMatchingJpgs(traj, outdir):
    try:
        datadir = os.getenv('DATADIR')
    except Exception:
        datadir='/home/ec2-user/prod/data'
    with open(os.path.join(datadir, 'singleJpgs.csv')) as inf:
        jpgs = inf.readlines()

    with open(os.path.join(outdir, 'jpgs.lst'), 'w') as outf:
        for obs in traj.observations:
            statid = obs.station_id
            evtdate = jd2Date(obs.jdt_ref, dt_obj=True)
            compstr = statid + '_' + evtdate.strftime('%Y%m%d_%H%M%S')
            mtch=[line.strip() for line in jpgs if compstr[:-1] in line]
            if len(mtch) > 1: 
                for m in mtch:
                    fn = os.path.basename(m)
                    spls=fn.split('_')
                    dtstamp = datetime.strptime(spls[2] + '_' + spls[3], '%Y%m%d_%H%M%S')
                    if (evtdate - dtstamp).seconds < 10:
                        outf.write('{}\n'.format(m[0]))
                        break
            elif len(mtch) == 0:
                tmped = evtdate + timedelta(seconds=-10)
                compstr = statid + '_' + tmped.strftime('%Y%m%d_%H%M%S')
                mtch=[line.strip() for line in jpgs if compstr[:-1] in line]
                if len(mtch) > 0:
                    outf.write('{}\n'.format(mtch[0]))
            else: 
                outf.write('{}\n'.format(mtch[0]))


def fetchJpgsAndMp4s(traj, outdir):
    try:
        archdir = os.getenv('ARCHDIR')
    except Exception:
        archdir='/home/ec2-user/ukmon-shared/archive'

    print('getting camera details file')
    cinfo = cdet.SiteInfo()

    for obs in traj.observations:
        statid = obs.station_id
        fldr = cinfo.getFolder(statid)
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
    fl = sys.argv[1]
    if os.path.isdir(fl):
        generateExtraFiles(fl)
    else:
        with open(fl,'r') as inf:
            dirs = inf.readlines()
            for li in dirs:
                fl = li.split(',')[1]
                generateExtraFiles(fl)
