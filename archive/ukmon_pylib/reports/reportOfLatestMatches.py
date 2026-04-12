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

from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase


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


def getListOfNewMatches(dir_path):
    trajdb = TrajectoryDatabase('/tmp', purge_records=True)
    flist = glob.glob(os.path.join(dir_path, 'trajectories_*.db'))
    flist.sort()
    for fl in flist:
        tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print(f'{tstamp} processing {fl}')
        if trajdb.mergeTrajDatabase(fl):
            os.remove(fl)
        else:
            print('error')

    if os.getenv('TESTMODE').lower() == 'true':
        trajdir = 'matches/distrib/test'
    else:
        trajdir = 'matches/RMSCorrelate'

    cur = trajdb.dbhandle.execute('select traj_file_path from trajectories where status=1')
    newtrajs = cur.fetchall()
    trajdb.closeTrajDatabase()

    newdirs = []
    for traj in newtrajs:
        newdirs.append(os.path.join(trajdir, traj[0]))

    return newdirs


def findNewMatches(dir_path, out_path, offset, repdtstr):

    newdirs = getListOfNewMatches(dir_path)
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

    srcdir = sys.argv[1]
    outdir = sys.argv[2]
    offset = sys.argv[3]
        
    # arguments dblocation, datadir, days ago, rundate eg 20220524
    findNewMatches(srcdir, outdir, offset, repdtstr)
