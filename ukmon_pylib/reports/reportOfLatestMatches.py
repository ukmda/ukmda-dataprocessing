#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import numpy
import csv
import fileformats.CameraDetails as cd
from traj.extraDataFiles import getVMagCodeAndStations
import json


def getTrajPaths(trajdict):
    trajpaths=[]
    fullnames=[]
    for traj in trajdict:
        fullnames.append(trajdict[traj]['traj_file_path'])
        pth, _ = os.path.split(trajdict[traj]['traj_file_path'])
        trajpaths.append(pth)
    return trajpaths, fullnames


def getListOfNewMatches(dir_path, tfile = 'processed_trajectories.json', prevtfile = 'prev_processed_trajectories.json'):
    with open(os.path.join(dir_path, tfile), 'r') as inf:
        trajs = json.load(inf)
    with open(os.path.join(dir_path, prevtfile), 'r') as inf:
        ptrajs = json.load(inf)
    
    newtrajs = {k:v for k,v in trajs['trajectories'].items() if k not in ptrajs['trajectories']}
    print(len(newtrajs))
    newdirs, _ = getTrajPaths(newtrajs)  
    return newdirs


def findNewMatches(dir_path, out_path):
    newdirs = getListOfNewMatches(dir_path, 'processed_trajectories.json.bigserver', 'prev_processed_trajectories.json.bigserver')
    # load camera details
    cinf = cd.SiteInfo()

    matchlist = os.path.join(out_path, 'dailyreports', datetime.datetime.now().strftime('%Y%m%d.txt'))
    with open(matchlist, 'w') as outf:
        for trajdir in newdirs:
            trajdir = trajdir.replace('/data/','/ukmon-shared/matches/')
            bestvmag, shwr, stationids = getVMagCodeAndStations(trajdir)
            stations=[]
            for statid in stationids:
                _,_,_,_,loc = cinf.GetSiteLocation(statid.encode('utf-8'))
                locbits = loc.split('/')
                stations.append(locbits[0])

            _, dname = os.path.split(trajdir)
            tstamp = datetime.datetime.strptime(dname[:15],'%Y%m%d_%H%M%S').timestamp()
            outstr = '{},{:s},{:s},{:.1f}'.format(int(tstamp), trajdir, shwr, bestvmag)

            for f in stations:
                if len(f) < 4:
                    break
                outstr = outstr + ',' + f
            outstr = outstr.strip()
            print(outstr)
            outf.write('{}\n'.format(outstr))

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
            
        return 


if __name__ == '__main__':
    findNewMatches(sys.argv[1], sys.argv[2])
