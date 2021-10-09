#
# Search for Fireballs in the archive
# Default magnitude -4 or greater (either abs or observed)
#

import sys
#from fileformats import UOFormat as uof
from fileformats import UAFormats as uaf


def findVisFireballs(idxfile, mag=-4):
    dets=uaf.DetectedCsv(idxfile)
    fbs = dets.selectByMag(minMag = mag)
    print(fbs)
    return


if __name__ == '__main__':
    idxfile = sys.argv[1]
    if len(sys.argv) > 2:
        mag = float(sys.argv[2])
    else:
        mag = -4
    findVisFireballs(idxfile, mag)
