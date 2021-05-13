#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import glob
from stat import S_ISREG, ST_MTIME, ST_MODE
import fileformats.CameraDetails as cd


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
                replist = glob.glob1(os.path.join(dir_path, ee[1]), '*report*.txt')[0]
                with open(os.path.join(dir_path, ee[1], replist), 'r') as repf:
                    lis = repf.readlines()
                stations=[]
                for i in range(len(lis)):
                    if "Timing offsets (from input data):" in lis[i]:
                        while len(lis[i].strip()) > 0:
                            i=i+1
                            spls = lis[i].strip().split(':')
                            if len(spls[0]) > 1:
                                _,_,_,_,loc = cinf.GetSiteLocation(spls[0].encode('utf-8'))
                                locbits = loc.split('/')
                                stations.append(locbits[0])

                _,dname = os.path.split(ee[1])
                outstr = '{},{:s}'.format(ee[0], dname)
                for f in stations:
                    if len(f) < 4:
                        break
                    outstr = outstr + ',' + f
                outstr = outstr.strip()
                print(outstr)
                outf.write('{}\n'.format(outstr))
    return 


if __name__ == '__main__':
    if len(sys.argv) > 2:
        targdate = datetime.datetime.strptime(sys.argv[2],'%Y%m%d')
    else:
        targdate = datetime.datetime.now()
    findNewMatches(sys.argv[1], targdate)
