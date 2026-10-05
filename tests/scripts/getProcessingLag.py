# find the lag between solution and data arrival

import os
import json
import sys
import datetime
import glob
import numpy as np

from wmpl.Utils.TrajConversions import jd2Date
from wmpl.Utils.Pickling import loadPickle

srcdatapath = '/srv/meteor/rms/gmn/extracted_data'
srcdatapath_ro = '/srv/meteor_ro/rms/gmn/extracted_data'
locsrcdatapath = '/home/mmcintyre/data'


def getListOfPickles(dtstr):
    dir_path = f'{srcdatapath}/trajectories/{dtstr[:4]}/{dtstr[:6]}/{dtstr[:8]}'
    picklist = []
    for root, _, files in os.walk(dir_path):
        pf = [f for f in files if '.pickle' in f]
        if len(pf) > 0:
            picklist.append(os.path.join(root, pf[0]))
    picklist.sort()
    return picklist


def getSaveDate(picklefile):
    traj = loadPickle(*os.path.split(picklefile))
    pickledate = traj.save_date.replace(tzinfo=datetime.timezone.utc)
    return pickledate


def getTrajDetails(trajfilename, detailed=False):
    if os.path.isfile(trajfilename):
        traj = loadPickle(*os.path.split(trajfilename))
    else:
        return False, False
    trajdt = jd2Date(traj.jdt_ref, dt_obj=True, tzinfo=datetime.timezone.utc)
    if hasattr(traj, 'save_date'):
        if detailed:
            print('using save_date')
        pickledate = traj.save_date.replace(tzinfo=datetime.timezone.utc)
    else:
        pickledate = datetime.datetime.fromtimestamp(os.path.getmtime(trajfilename)).replace(tzinfo=datetime.timezone.utc)
    latestdate = datetime.datetime(2000,1,1).replace(tzinfo=datetime.timezone.utc)
    for obs in traj.observations:
        if detailed:
            print(f'-----\n{obs.station_id}')
        ff_name = json.loads(obs.comment)['ff_name']
        if detailed:
            print(f'trying {trajdt} with {ff_name}')
        ftppath = os.path.join(srcdatapath, obs.station_id, f'{obs.station_id}_{trajdt.strftime("%Y%m%d")}')
        flist=glob.glob(f'{ftppath}*/*')
        ftpf = [x for x in flist if 'FTP' in x]
        if len(ftpf) > 0:
            for fil in ftpf:
                lis = open(fil, 'r').readlines()
                if detailed:
                    print(f'got ftpfile {fil}')
                mtch = [li for li in lis if ff_name in li]
                if len(mtch) > 0:
                    flagf = [x for x in flist if 'flag' in x]
                    cdate = datetime.datetime.fromtimestamp(os.path.getmtime(flagf[0])).replace(tzinfo=datetime.timezone.utc)
                    if detailed:
                        print(f' {flagf[0]} create date {cdate}')
                    latestdate = max(cdate, latestdate)
        adjdt = trajdt + datetime.timedelta(days=-1)
        if detailed:
            print(f'trying {adjdt} with {ff_name}')
        ftppath = os.path.join(srcdatapath, obs.station_id, f'{obs.station_id}_{adjdt.strftime("%Y%m%d")}')
        flist=glob.glob(f'{ftppath}*/*')
        ftpf = [x for x in flist if 'FTP' in x]
        if len(ftpf) > 0:
            for fil in ftpf:
                lis = open(fil, 'r').readlines()
                if detailed:
                    print(f'got ftpfile {fil}')
                mtch = [li for li in lis if ff_name in li]
                if len(mtch) > 0:
                    flagf = [x for x in flist if 'flag' in x]
                    cdate = datetime.datetime.fromtimestamp(os.path.getmtime(flagf[0])).replace(tzinfo=datetime.timezone.utc)
                    if detailed:
                        print(f' {flagf[0]} create date {cdate}')
                    latestdate = max(cdate, latestdate)
    return latestdate, pickledate


def getLastPeriod(picklist, hours=24):
    latest = picklist[-1]
    latestdate = datetime.datetime.strptime(latest[:19], '%Y%m%d_%H%M%S.%f')
    fromdt = latestdate + datetime.timedelta(hours=-hours)
    filtlist = [p for p in picklist if datetime.datetime.strptime(p[:19], '%Y%m%d_%H%M%S.%f') > fromdt]
    return filtlist


if __name__ == '__main__':
    if len(sys.argv) < 2:
        picklist = os.listdir('.')
        picklist.sort()
        picklist = [p for p in picklist if '.pickle' in p and 'processing' not in p]
        if len(picklist) == 0:
            exit(0)
        picklist = getLastPeriod(picklist, 24)
        lags=[]
        for fname in picklist:
            if os.path.isfile(fname):
                uploaddate, cdate = getTrajDetails(fname)
                if uploaddate:
                    lag = cdate - uploaddate
                    if lag > datetime.timedelta(days=10):
                        lag = datetime.timedelta(days=0)
                    if cdate < uploaddate:
                        lag = datetime.timedelta(hours=0)
                    print(f'{fname:50} {lag}')
                    lags.append(lag.total_seconds()/3600)
        meanlag = np.mean(lags)
        stdlag = np.std(lags)
        maxlag = np.max(lags)
        minlag = np.min(lags)
#        print(f'statistics: mean {meanlag:.3}, std dev {stdlag:.3}, max/min lag {maxlag:.3}/{minlag:.3}')
    else:
        inputfname = sys.argv[1]
        if inputfname == 'live':
            end_dt = datetime.datetime.now()
            start_dt = end_dt - datetime.timedelta(days=2)
            act_start_dt = start_dt
            results = []
            while start_dt <= end_dt:
                dtstr = start_dt.strftime('%Y%m%d')
                print(f'processing {dtstr}')
                picklist = getListOfPickles(dtstr)
                for pick in picklist:
                    shortpick = pick.split('/')[-2]
                    if datetime.datetime.strptime(shortpick[:15], '%Y%m%d_%H%M%S') < act_start_dt:
                        continue
                    uploaddate, cdate = getTrajDetails(pick, detailed=False)
                    lag = cdate - uploaddate
                    if lag > datetime.timedelta(days=10):
                        lag = datetime.timedelta(days=0)
                    if lag < datetime.datetime(minutes=1):
                        lag = datetime.timedelta(days=0)
                    results.append([shortpick, lag, uploaddate, cdate])
                start_dt += datetime.timedelta(days=1)
            with open('live_lags.csv', 'w') as outf:
                for rw in results:
                    outf.write(f'{rw[0]},{rw[1]},{rw[2]},{rw[3]}\n')
        else:            
            usero = 0
            if len(sys.argv) > 2:
                usero = int(sys.argv[2])
            if 'trajectory.pickle' not in inputfname:
                trajname = inputfname[:15] + '_trajectory.pickle'
                if usero == 0:
                    print('using local path')
                    fname = os.path.join(locsrcdatapath, 'trajectories', trajname[:4], trajname[:6], trajname[:8], inputfname, trajname)
                else:
                    print('using remote path')
                    fname = os.path.join(srcdatapath, 'trajectories', trajname[:4], trajname[:6], trajname[:8], inputfname, trajname)
            else:
                fname = inputfname
            if not os.path.isfile(fname):
                print('pickle not found')
                exit(0)
            detailed = False
            if len(sys.argv) > 3:
                detailed=True
            uploaddate, cdate = getTrajDetails(fname, detailed=detailed)
            print(f'uploaddate {uploaddate}')
            print(f'pickle date {cdate}')
            lag = cdate - uploaddate
            if lag > datetime.timedelta(days=10):
                lag = datetime.timedelta(days=0)
            print(f'{fname:50} {lag}')
