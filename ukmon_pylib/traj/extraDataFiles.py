#
# Create additional information from pickled Trajectory file
#
import os
import sys
import glob

from wmpl.Utils.Pickling import loadPickle 
from wmpl.Utils.TrajConversions import jd2Date
from datetime import datetime, timedelta
from traj.ufoTrajSolver import createAdditionalOutput, calcAdditionalValues, loadMagData


def generateExtraFiles(outdir):

    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    traj.save_results = True

    createAdditionalOutput(traj, outdir)
    findMatchingJpgs(traj, outdir)
    return


def getBestView(outdir):
    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    _, statids, vmags = loadMagData(traj)
    bestvmag = min(vmags)
    beststatid = statids[vmags.index(bestvmag)]
    imgfn = glob.glob1(outdir, '*{}*.jpg'.format(beststatid))
    if len(imgfn) > 0:
        bestimg = imgfn[0]
    else:
        with open(os.path.join(outdir, 'jpgs.lst')) as inf:
            lis = inf.readlines()
        bestimg=''
        worstmag = max(vmags)
        for mag, stat in zip(vmags, statids):
            res=[stat in ele for ele in lis]    
            imgfn = lis[res is True].strip()
            if mag <= worstmag:
                if len(imgfn) > 0:
                    bestimg = imgfn

    return bestimg


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
