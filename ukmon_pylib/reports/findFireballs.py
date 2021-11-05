#
# Search for Fireballs in the archive
# Default magnitude -4 or greater (either abs or observed)
#

import sys
import os
import pandas as pd
from fileformats import UOFormat as uof
from fileformats import UAFormats as uaf


def findMatchedFireballs(df, outdir = None, mag=-4):
    fbs = df[df['_mag'] < -3.999]
    fbs = fbs.sort_values(by='_mag')
    newm=pd.concat([fbs['url'],fbs['_mag'], fbs['_stream']], axis=1, keys=['url','mag','shower'])
    if outdir is not None:
        outf = os.path.join(outdir, 'fblist.txt')
        newm.to_csv(outf, index=False, header=False)
    return fbs


if __name__ == '__main__':
    datadir = os.getenv('DATADIR')
    if datadir == '' or datadir is None:
        print('export DATADIR first')
        exit(1)

    yr = int(sys.argv[1])
    #print(yr)
    fname = os.path.join(datadir, 'matched','matches-full-{}.csv'.format(yr))
    if os.path.isfile(fname):
        with open(fname) as inf:
            df = pd.read_csv(inf)
    else:
         exit(0)
    
    outdir = sys.argv[2]
    if len(sys.argv) > 3:
        mag = float(sys.argv[3])
    else:
        mag = -4
    fbs = findMatchedFireballs(df, outdir, mag)
