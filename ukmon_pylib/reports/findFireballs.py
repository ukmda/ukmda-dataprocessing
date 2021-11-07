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


def findMatchedFireballs(df, outdir = None, mag=-4):
    fbs = df[df['_mag'] < -3.999]
    fbs = fbs.sort_values(by='_mag')
    newm=pd.concat([fbs['url'],fbs['_mag'], fbs['_stream'], fbs['_vg'], fbs['mass'], fbs['_mjd']], axis=1, keys=['url','mag','shower','vg','mass','mjd'])
    if outdir is not None:
        outf = os.path.join(outdir, 'fblist.txt')
        newm.to_csv(outf, index=False, header=False, columns=['url','mag','shower'])
    return newm


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
    createMDFiles(fbs, outdir, '/home/ec2-user/ukmon-shared/matches/')
