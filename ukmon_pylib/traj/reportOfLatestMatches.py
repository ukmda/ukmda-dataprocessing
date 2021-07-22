#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import numpy
import csv
from stat import S_ISREG, ST_MTIME, ST_MODE
import fileformats.CameraDetails as cd
from traj.extraDataFiles import getVMagCodeAndStations


def findNewMatches(dir_path, targdate):
    # get all entries in the directory
    entries = (os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path))
    # Get their stats
    entries = ((os.stat(path), path) for path in entries)

    # set date range
    now = targdate
    yday = targdate #  + datetime.timedelta(days=-1)
    yday = yday.replace(hour=7, minute=30, second=0, microsecond=0)
    yday = yday.timestamp()

    # load camera details
    cinf = cd.SiteInfo()

    print('----------------------')
    # leave only regular files, insert creation date
    entries = ((stat[ST_MTIME], path)
            for stat, path in entries if not S_ISREG(stat[ST_MODE]))

    matchlist = os.path.join(dir_path, '../dailyreports/' + now.strftime('%Y%m%d.txt'))    
    with open(matchlist, 'w') as outf:
        for ee in entries:
            if ee[0] > yday:
                bestvmag, shwr, stationids = getVMagCodeAndStations(os.path.join(dir_path, ee[1]))
                stations=[]
                for statid in stationids:
                    _,_,_,_,loc = cinf.GetSiteLocation(statid.encode('utf-8'))
                    locbits = loc.split('/')
                    stations.append(locbits[0])

                _,dname = os.path.split(ee[1])
                outstr = '{},{:s},{:s},{:.1f}'.format(ee[0], dname, shwr, bestvmag)
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
    if len(sys.argv) > 2:
        targdate = datetime.datetime.strptime(sys.argv[2],'%Y%m%d')
    else:
        targdate = datetime.datetime.now()
    findNewMatches(sys.argv[1], targdate)
