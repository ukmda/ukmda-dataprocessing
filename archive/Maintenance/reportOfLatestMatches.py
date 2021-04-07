#
# create record of matches found in the last day (may contain older data now matched)
#

import os
import sys
import datetime
import glob
from stat import S_ISREG, ST_CTIME, ST_MODE


def findNewMatches(dir_path, targdate):
    # get all entries in the directory
    entries = (os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path))
    # Get their stats
    entries = ((os.stat(path), path) for path in entries)

    # get now and noon the previous day
#    now = datetime.datetime.now()
    now = targdate
    yday = now + datetime.timedelta(days=-1)
    yday = yday.replace(hour=9, minute=0, second=0, microsecond=0)
    yday = yday.timestamp()

    print('----------------------')
    # leave only regular files, insert creation date
    entries = ((stat[ST_CTIME], path)
            for stat, path in entries if not S_ISREG(stat[ST_MODE]))

    matchlist = os.path.join(dir_path, '../dailyreports/' + now.strftime('%Y%m%d.txt'))    
    with open(matchlist, 'w') as outf:
        for ee in entries:
            if ee[0] > yday:
                ftplist =glob.glob1(os.path.join(dir_path, ee[1]), 'FTP*.txt')
                _,dname = os.path.split(ee[1])
                outstr = '{},{:s}'.format(ee[0], dname)
                for f in ftplist:
                    spls = f.split('_')
                    outstr = outstr + ',' +spls[1]
                outstr = outstr 
                print(outstr)
                outf.write('{}\n'.format(outstr))
    return 


if __name__ == '__main__':
    if len(sys.argv) > 2:
        targdate = datetime.datetime.strptime(sys.argv[2],'%Y%m%d')
    else:
        targdate = datetime.datetime.now()
    findNewMatches(sys.argv[1], targdate)
