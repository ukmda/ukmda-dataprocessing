# Copyright (C) 2018-2023 Mark McIntyre
#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import numpy
import csv
import shutil
import tempfile
import boto3
import glob

from traj.pickleAnalyser import getVMagCodeAndStations
from reports.CameraDetails import findSite, loadLocationDetails

from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase, ObservationsDatabase


def processLocalFolder(trajdir, basedir):
    # load camera details
    caminfo = loadLocationDetails()
    caminfo = caminfo[caminfo.active==1]

    bestvmag, shwr, stationids = getVMagCodeAndStations(trajdir)
    stations=[]
    for statid in stationids:
        loc = findSite(statid, caminfo) 
        stations.append(loc)

    _, dname = os.path.split(trajdir)
    realtraj = trajdir[trajdir.find('tra'):]
    realtraj = basedir + '/' + realtraj
    if '.pickle' in realtraj:
        realtraj, _ = os.path.split(realtraj)
    tstamp = datetime.datetime.strptime(dname[:15],'%Y%m%d_%H%M%S').timestamp()
    outstr = '{},{:s},{:s},{:.1f},'.format(int(tstamp), realtraj, shwr, bestvmag)
    outstr = outstr + ';'.join(stations)
    return outstr


def getListOfNewMatches(dir_path, db_path='/tmp', rundate=None):
    os.makedirs(db_path, exist_ok=True)
    db_name = f'{rundate}_trajectories.db' if rundate else 'trajectories.db'
    dailydb = TrajectoryDatabase(db_path=db_path, db_name=db_name, purge_records=True)
    flist = glob.glob(os.path.join(dir_path, 'trajectories_*.db'))
    flist.sort()
    for fl in flist:
        tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print(f'{tstamp} processing {fl}')
        if dailydb.mergeTrajDatabase(fl):
            os.remove(fl)
        else:
            print('error')

    if os.getenv('TESTMODE').lower() == 'true':
        trajdir = 'matches/distrib/test'
    else:
        trajdir = 'matches/RMSCorrelate'

    cur = dailydb.dbhandle.execute('select traj_file_path from trajectories where status=1')
    newtrajs = cur.fetchall()

    if len(newtrajs) > 0:
        # now get a list of logically-deleted trajs from the current master DB
        datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))

        # get the date range for the new trajectories
        cur = dailydb.dbhandle.execute('select min(jdt_ref), max(jdt_ref) from trajectories where status=1')    
        vals = cur.fetchall()
        jdt_beg = float(vals[0][0])
        jdt_end = float(vals[0][1])

        # retrieve a list of logically-deleted trajectories from within that date range
        masterdb_path = os.path.join(datadir, 'distrib')
        masterdb = TrajectoryDatabase(db_path=masterdb_path)
        cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
        deltrajs = cur.fetchall()
        masterdb.closeTrajDatabase()

        # iterate over the delete list and update the daily db and new traj list accordingly
        for testtr in deltrajs:
            if testtr in newtrajs:
                sqlstr = f'update trajectories set status=0 where "traj_file_path={testtr[0]}";'
                dailydb.dbhandle.execute(sqlstr)
                newtrajs.pop(newtrajs.index(testtr))

    dailydb.closeTrajDatabase()
    
    newdirs = []
    for traj in newtrajs:
        newdirs.append(os.path.join(trajdir, traj[0]))

    return newdirs


def updatePairedDB(dir_path, db_path='/tmp', rundate=None):
    os.makedirs(db_path, exist_ok=True)
    db_name = f'{rundate}_observations.db' if rundate else 'observations.db'
    obsdb = ObservationsDatabase(db_path=db_path, db_name=db_name, purge_records=True)
    flist = glob.glob(os.path.join(dir_path, 'observations_*.db'))
    flist.sort()
    for fl in flist:
        tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print(f'{tstamp} processing {fl}')
        if obsdb.mergeObsDatabase(fl):
            os.remove(fl)
        else:
            print('error')

    cur = obsdb.dbhandle.execute('select count(*) from paired_obs where status=1')
    obscount = cur.fetchall()

    return obscount


def findNewMatches(dir_path, out_path, offset, repdtstr):
    daily_path = os.path.join(os.path.split(dir_path)[0], 'dailydbs')
    newdirs = getListOfNewMatches(dir_path, daily_path, rundate=repdtstr)
    # load camera details
    caminfo = loadLocationDetails()
    caminfo = caminfo[caminfo.active==1]

    if repdtstr is not None:
        repdt = datetime.datetime.strptime(repdtstr, '%Y%m%d')
    else:
        repdt = datetime.datetime.now() - datetime.timedelta(int(offset))

    os.makedirs(out_path, exist_ok=True)
    # create filename. Allow for three reruns in a day
    matchlist = os.path.join(out_path, repdt.strftime('%Y%m%d.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, repdt.strftime('%Y%m%d_1.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, repdt.strftime('%Y%m%d_2.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, repdt.strftime('%Y%m%d_3.txt'))

    s3 = boto3.client('s3')
    srcbucket=os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    tmpdir = tempfile.mkdtemp()
    with open(matchlist, 'w') as outf:
        for trajdir in newdirs:
            trajdir = trajdir[trajdir.find('matches'):]
            trajpath, picklename = os.path.split(trajdir)
            localpick = os.path.join(tmpdir, picklename)
            try:
                s3.download_file(srcbucket, trajdir, localpick)
                bestvmag, shwr, stationids = getVMagCodeAndStations(localpick)
            except:
                print(f'unable to find {trajdir}')
                bestvmag, shwr, stationids = 0,'',['']
            stations=[]
            for statid in stationids:
                loc = findSite(statid, caminfo)
                stations.append(loc)

            _, dname = os.path.split(trajdir)
            tstamp = datetime.datetime.strptime(dname[:15],'%Y%m%d_%H%M%S').timestamp()
            outstr = '{},{:s},{:s},{:.1f},'.format(int(tstamp), trajpath, shwr, bestvmag)
            outstr = outstr + ';'.join(stations)
            outstr = outstr.strip()
            #print(outstr)
            outf.write('{}\n'.format(outstr))
    
    shutil.rmtree(tmpdir)

    # sort the data by magnitude
    with open(matchlist,'r') as f:
        iter=csv.reader(f, delimiter=',')
        data = [data for data in iter]
        data_array=numpy.asarray(data)
        sarr = sorted(data_array, key=lambda a_entry: float(a_entry[3]))

    with open(matchlist, 'w') as outf:
        for li in sarr:
            lastfld = li[len(li)-1]
            for fld in li:
                outf.write('{}'.format(fld))
                if fld != lastfld:
                    outf.write(',')
            outf.write('\n')

    # finally, create a "latest.txt" as well
    latestlist = os.path.join(out_path, 'latest.txt')
    shutil.copy(matchlist, latestlist)
    return 


if __name__ == '__main__':
    repdtstr = None
    if len(sys.argv) > 4:
        repdtstr = sys.argv[4]

    cand_db_dir = sys.argv[1]
    daily_db_dir = sys.argv[2]
    offset = sys.argv[3]
        
    # arguments dblocation, datadir, days ago, rundate eg 20220524
    findNewMatches(cand_db_dir, daily_db_dir, offset, repdtstr)
    # update the daily database of paired observations
    daily_db_dir = os.path.join(os.path.split(cand_db_dir)[0], 'dailydbs')
    updatePairedDB(cand_db_dir, daily_db_dir, repdtstr)
