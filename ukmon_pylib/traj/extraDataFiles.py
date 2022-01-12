#
# Create additional information from pickled Trajectory file
#
import os
import sys
import glob
import shutil
import platform

from wmpl.Utils.Pickling import loadPickle 
from wmpl.Utils.TrajConversions import jd2Date
from datetime import datetime, timedelta
from traj.ufoTrajSolver import createAdditionalOutput, calcAdditionalValues, loadMagData
from fileformats import CameraDetails as cdet


def generateExtraFiles(outdir, skipimgs = False):
    outdir=os.path.normpath(outdir)
    try:
        picklefile = glob.glob1(outdir, '*.pickle')[0]
    except Exception:
        print('no pickle found in ', outdir)
    else:
        traj = loadPickle(outdir, picklefile)
        traj.save_results = True

        createAdditionalOutput(traj, outdir)
        if skipimgs is False:
            findMatchingJpgs(traj, outdir)
            findMatchingMp4s(traj, outdir)
    return


def getBestView(outdir):
    try:
        picklefile = glob.glob1(outdir, '*.pickle')[0]
    except Exception:
        print('no picklefile in ', outdir)
        return ''
    else:
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
    _, bestvmag, _, _, cod, _, _, _, _, _, _, stations = calcAdditionalValues(traj)
    return bestvmag, cod, stations


def findMatchingJpgs(traj, outdir):
    try:
        datadir = os.getenv('DATADIR')
    except Exception:
        datadir='/home/ec2-user/prod/data'

    jpgs = None
    # file to write JPGs html to, for performance benefits
    jpghtml = open(os.path.join(outdir, 'jpgs.html'), 'w')
    # loop over observations adding jpgs to the listing file
    with open(os.path.join(outdir, 'jpgs.lst'), 'w') as outf:
        for obs in traj.observations:
            statid = obs.station_id
            evtdate = jd2Date(obs.jdt_ref, dt_obj=True)
            if jpgs is None:
                with open(os.path.join(datadir, 'singleJpgs-{}.csv'.format(evtdate.year))) as inf:
                    jpgs = inf.readlines()
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
                    jpghtml.write(f'<a href="/{mtch[0]}"><img src="/{mtch[0]}" width="20%"></a>\n')
            else: 
                outf.write('{}\n'.format(mtch[0]))
                jpghtml.write(f'<a href="/{mtch[0]}"><img src="/{mtch[0]}" width="20%"></a>\n')
    jpghtml.close()


def findMatchingMp4s(traj, outdir):
    archdir = os.getenv('ARCHDIR')
    if archdir is None:
        archdir='/home/ec2-user/ukmon-shared/archive'

    print('getting camera details file')
    cinfo = cdet.SiteInfo()

    for obs in traj.observations:
        statid = obs.station_id
        fldr = cinfo.getFolder(statid)
        #print(statid, fldr)
        evtdate = jd2Date(obs.jdt_ref, dt_obj=True)

        #print('station {} event {} '.format(statid, evtdate.strftime('%Y%m%d-%H%M%S')))
        # if the event is after midnight the folder will have the previous days date
        if evtdate.hour < 12:
            evtdate += timedelta(days=-1)
        yr = evtdate.year
        ym = evtdate.year * 100 + evtdate.month
        ymd = ym *100 + evtdate.day

        #print('getting mp4s')
        thispth = '{:s}/{:04d}/{:06d}/{:08d}/'.format(fldr, yr, ym, ymd)
        #print(thispth)
        srcpath = os.path.join(archdir, thispth)
        flist = glob.glob1(srcpath, 'FF*.mp4')
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
            try: 
                shutil.copy2(srcfil, outdir)
            except FileNotFoundError:
                pass
        else:
            pass
            #print('no mp4s in {}'.format(srcpath))

        print('R90 CSV, KML and FTPDetect file')
        try:
            flist=glob.glob1(srcpath, '*.csv')
            for f in flist:
                shutil.copy2(os.path.join(srcpath, f), outdir)
            flist=glob.glob1(srcpath, '*.kml')
            for f in flist:
                shutil.copy2(os.path.join(srcpath, f), outdir)
            flist = glob.glob1(srcpath, "FTPdetectinfo*.txt")
            for fil in flist:
                shutil.copy2(os.path.join(srcpath, f), outdir)
        except:
            continue
    mp4s=glob.glob1(outdir, "*.mp4")
    if len(mp4s) > 0:
        _, orbdir = os.path.split(outdir)
        #print(outdir, orbdir)
        fullpth='reports/{}/orbits/{}/{}/{}'.format(orbdir[:4], orbdir[:6], orbdir[:8], orbdir)
        mpghtml = open(os.path.join(outdir, 'mpgs.html'), 'w')
        with open(os.path.join(outdir, 'mpgs.lst'), 'a') as outf:
            for mp4 in mp4s:
                mp4name = f'{fullpth}/{mp4}'
                outf.write(f'{mp4name}\n')
                mpghtml.write(f'<a href="/{mp4name}"><video width="20%"><source src="/{mp4name}" type="video/mp4"></video></a>\n')
        mpghtml.close
    return


if __name__ == '__main__':
    fl = sys.argv[1]
    skipimgs = False
    if platform.system() == 'Windows':
        skipimgs = True

    if os.path.isdir(fl):
        generateExtraFiles(fl, skipimgs=skipimgs)
    else:
        with open(fl,'r') as inf:
            dirs = inf.readlines()
            for li in dirs:
                fl = li.split(',')[1]
                generateExtraFiles(fl, skipimgs=skipimgs)
