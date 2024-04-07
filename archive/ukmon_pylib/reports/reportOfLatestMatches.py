# Copyright (C) 2018-2023 Mark McIntyre
#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import numpy
import csv
import json
import shutil
import tempfile
import boto3

from traj.pickleAnalyser import getVMagCodeAndStations
from reports.CameraDetails import findSite, loadLocationDetails


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


def getTrajPaths(trajdict):
    trajpaths=[]
    fullnames=[]
    for traj in trajdict:
        fullnames.append(trajdict[traj]['traj_file_path'])
        pth, _ = os.path.split(trajdict[traj]['traj_file_path'])
        trajpaths.append(pth)
    return trajpaths, fullnames


def getListOfNewMatches(dir_path, tfile, prevtfile):
    with open(os.path.join(dir_path, tfile), 'r') as inf:
        trajs = json.load(inf)
    with open(os.path.join(dir_path, prevtfile), 'r') as inf:
        ptrajs = json.load(inf)    
    newtrajs = {k:v for k,v in trajs['trajectories'].items() if k not in ptrajs['trajectories']}
    #print(len(newtrajs))
    _, newdirs = getTrajPaths(newtrajs)  
    return newdirs


def findNewMatches(dir_path, out_path, offset, repdtstr, dbname):
    prevdbname = 'prev_' + dbname
    newdirs = getListOfNewMatches(dir_path, dbname, prevdbname)
    # load camera details
    caminfo = loadLocationDetails()
    caminfo = caminfo[caminfo.active==1]

    if repdtstr is not None:
        repdt = datetime.datetime.strptime(repdtstr, '%Y%m%d')
    else:
        repdt = datetime.datetime.now() - datetime.timedelta(int(offset))

    os.makedirs(os.path.join(out_path, 'dailyreports'), exist_ok=True)
    # create filename. Allow for three reruns in a day
    matchlist = os.path.join(out_path, 'dailyreports', repdt.strftime('%Y%m%d.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, 'dailyreports', repdt.strftime('%Y%m%d_1.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, 'dailyreports', repdt.strftime('%Y%m%d_2.txt'))
    if os.path.isfile(matchlist) is True:
        matchlist = os.path.join(out_path, 'dailyreports', repdt.strftime('%Y%m%d_3.txt'))

    s3 = boto3.client('s3')
    srcbucket=os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    tmpdir = tempfile.mkdtemp()
    with open(matchlist, 'w') as outf:
        for trajdir in newdirs:
            trajdir = trajdir[trajdir.find('matches'):]
            trajpath, picklename = os.path.split(trajdir)
            localpick = os.path.join(tmpdir, picklename)
            s3.download_file(srcbucket, trajdir, localpick)
            try:
                bestvmag, shwr, stationids = getVMagCodeAndStations(localpick)
            except:
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
    latestlist = os.path.join(out_path, 'dailyreports', 'latest.txt')
    shutil.copy(matchlist, latestlist)
    return 


if __name__ == '__main__':
    repdtstr = None
    dbname = None
    if len(sys.argv) > 4:
        repdtstr = sys.argv[4]
    if len(sys.argv) > 5:
        dbname = sys.argv[5]
    else:
        dbname = 'processed_trajectories.json.bigserver'
        
    # arguments dblocation, datadir, days ago, rundate eg 20220524, full path to database
    findNewMatches(sys.argv[1], sys.argv[2], sys.argv[3], repdtstr, dbname)
