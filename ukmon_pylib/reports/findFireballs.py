#
# Search for Fireballs in the archive
# Default magnitude -4 or greater (either abs or observed)
#

import sys
import os
import pandas as pd
from fileformats import UOFormat as uof
from fileformats import UAFormats as uaf


def findVisFireballs(idxfile, mag=-4):
    dets=uaf.DetectedCsv(idxfile)
    fbs = dets.selectByMag(minMag=mag, filterbadav=False)
    singlefbs = pd.DataFrame(zip(fbs['LocalTime'], fbs['Mag'],fbs['Group'],fbs['AV(deg/s)']), columns=['LocalTime','Mag','Group','AV'])
    singlefbs = singlefbs.sort_values(by=['LocalTime'])
    return fbs


def findMatchedFireballs(idxfile2, mag=-4):
    dets=uof.MatchedCsv('/home/ec2-user/prod/data/UKMON-all-matches.csv')
    fbs = uof.selectByMag(minMag=mag)
    return fbs


if __name__ == '__main__':
    idxfile = os.path.expanduser(sys.argv[1])
    if len(sys.argv) > 2:
        mag = float(sys.argv[2])
    else:
        mag = -4
    fbs = findVisFireballs(idxfile, mag)

    print(fbs)
