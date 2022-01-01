#
# Search for Fireballs in the archive
# Default magnitude -4 or greater (either abs or observed)
#

import sys
import os
import pandas as pd
from traj.extraDataFiles import getBestView
from wmpl.Utils.TrajConversions import jd2Date


def createMDFiles(fbs, outdir, matchdir):
    for _, fb in fbs.iterrows(): 
        loctime = jd2Date(fb.mjd + 2400000.5, dt_obj=True)
        trajdir=loctime.strftime("%Y%m%d_%H%M%S.%f")[:-3] + "_UK"
        yr = trajdir[:4]
        ym = trajdir[:6]
        ymd = trajdir[:8]
        pickledir = os.path.join(matchdir, 'RMSCorrelate', 'trajectories', yr, ym, ymd, trajdir)
        bestimg = getBestView(pickledir)
        if bestimg[:4] != 'img/':
            pth, _ = os.path.split(fb.url)
        else:
            pth = fb.url[:fb.url.find('reports/')]
        bestimgurl = os.path.join(pth, bestimg)

        fname = loctime.strftime('%Y%m%d_%H%M%S') + '.md'
        with open(os.path.join(outdir,fname), 'w') as outf:
            outf.write('---\nlayout: fireball\n\n')
            outf.write('date: {}\n\n'.format(loctime.strftime('%Y-%m-%d %H:%M:%SZ')))
            outf.write('showerID: {}\n'.format(fb.shower))
            outf.write('bestmag: {:.1f}\n'.format(fb.mag))
            outf.write('mass: {:.5f}g\n'.format(fb.mass*1000))
            outf.write('vg: {:.2f}m/s\n'.format(fb.vg))
            outf.write('\n')
            outf.write('archive-url: {}\n'.format(fb.url))
            outf.write('bestimage: {}\n'.format(bestimgurl))
            outf.write('\n---\n')
    return


def findMatchedFireballs(df, outdir=None, mag=-4):
    fbs = df.sort_values(by='_mag')
    if mag == 999: 
        fbs = fbs.head(10)        
    else:
        fbs = fbs[fbs['_mag'] < mag]
    newm=pd.concat([fbs['url'],fbs['_mag'], fbs['_stream'], fbs['_vg'], fbs['mass'], fbs['_mjd']], axis=1, keys=['url','mag','shower','vg','mass','mjd'])
    return newm


if __name__ == '__main__':
    datadir = os.getenv('DATADIR')
    if datadir == '' or datadir is None:
        print('export DATADIR first')
        exit(1)

    yr = int(sys.argv[1])

    # check if month was passed in
    mth = None
    if yr > 9999:
        ym = sys.argv[1]
        yr = int(ym[:4])
        mth = int(ym[4:6])

    fname = os.path.join(datadir, 'matched','matches-full-{}.csv'.format(yr))
    if os.path.isfile(fname):
        with open(fname) as inf:
            df = pd.read_csv(inf)
    else:
        print('unable to load datafile')
        exit(0)
    
    outdir = sys.argv[2]
    shwr = sys.argv[3]
    if len(sys.argv) > 4:
        mag = float(sys.argv[4])
    else:
        mag = -3.9

    if shwr != 'ALL':
        df = df[df['_stream']==shwr]
    if mth is not None:
        df = df[df['_M_ut']==mth]

    fbs = findMatchedFireballs(df, outdir, mag)

    if len(fbs) > 0: 
        if outdir is not None:
            os.makedirs(outdir, exist_ok=True)
            outf = os.path.join(outdir, 'fblist.txt')
            fbs.to_csv(outf, index=False, header=False, columns=['url','mag','shower'])
        if shwr == 'ALL':
            createMDFiles(fbs, outdir, '/home/ec2-user/ukmon-shared/matches/')
