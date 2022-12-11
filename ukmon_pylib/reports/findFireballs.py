#
# Search for Fireballs and bright events in the archive
# Default magnitude -4 or greater (either abs or observed)
#

import sys
import os
import pandas as pd
import boto3
from tempfile import mkdtemp
from shutil import rmtree

from traj.pickleAnalyser import getBestView
from wmpl.Utils.TrajConversions import jd2Date


# 
# Manually mark a trajectoriy as a "fireball"
#
def markAsFireball(trajname, tof=True):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    yr=trajname[:4]
    if int(yr) > 2021:
        fname = os.path.join(datadir, 'matched','matches-full-{}.parquet.snap'.format(yr))
        if os.path.isfile(fname):
            # cant select cols here as we write them all back in a few lines
            df = pd.read_parquet(fname) 
        else:
            print('unable to load datafile')
            exit(0)
    else:
        print("can only be done for 2022 onwards")
        exit(0)
    print(f'setting {trajname} to {tof}')
    df.loc[df.orbname==trajname, ['isfb']] = tof
    df.to_parquet(fname, compression='snappy')
    csvfname = os.path.join(datadir, 'matched','matches-full-{}.csv'.format(yr))
    df.to_csv(csvfname, index=False)

    return 


#
# Create MD files for the Jekyll website
#
def createMDFiles(fbs, outdir, orbdir):
    s3 = boto3.client('s3')
    srcbucket=os.getenv('UKMONSHAREDBUCKET', default='s3://ukmon-shared')[5:]
    tmpdir = mkdtemp()
    for _, fb in fbs.iterrows(): 
        loctime = jd2Date(fb.mjd + 2400000.5, dt_obj=True)
        trajdir = fb.orbname
        yr = trajdir[:4]
        ym = trajdir[:6]
        ymd = trajdir[:8]
        pickledir = f'{orbdir}/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{trajdir}'
        try:
            picklename = trajdir[:15] +'_trajectory.pickle'
            fname = pickledir + '/' + picklename
            pickfile = os.path.join(tmpdir, picklename)
            s3.download_file(srcbucket, fname, pickfile)
        except:
            print(f'unable to collect {fname}')
        else:
            fname = pickledir + '/jpgs.lst'
            targfile = os.path.join(tmpdir, 'jpgs.lst')
            try:
                s3.download_file(srcbucket, fname, targfile)
                bestimg = getBestView(pickfile)
                #print(bestimg)
                if bestimg[:4] != 'img/':
                    pth, _ = os.path.split(fb.url)
                else:
                    pth = fb.url[:fb.url.find('reports/')]
                bestimgurl = os.path.join(pth, bestimg)
            except:
                print('unable to collect jpgs.lst')

            fname = loctime.strftime('%Y%m%d_%H%M%S') + '.md'
            if os.path.isfile(os.path.join(outdir,fname)):
                print('md file exists, not replacing it')
            else:
                with open(os.path.join(outdir,fname), 'w') as outf:
                    outf.write('---\nlayout: fireball\nsitemap: false\n\n')
                    outf.write('date: {}\n\n'.format(loctime.strftime('%Y-%m-%d %H:%M:%SZ')))
                    outf.write('showerID: {}\n'.format(fb.shower))
                    outf.write('bestmag: {:.1f}\n'.format(float(fb.mag)))
                    outf.write('mass: {:.5f}g\n'.format(float(fb.mass)*1000))
                    outf.write('vg: {:.2f}m/s\n'.format(float(fb.vg)))
                    outf.write('\n')
                    outf.write('archive-url: {}\n'.format(fb.url))
                    outf.write('bestimage: {}\n'.format(bestimgurl))
                    outf.write('\n---\n')
    rmtree(tmpdir)
    return


#
# Search the matched data for fireball events
#
def findMatchedFireballs(df, mag=-4):
    fbs = df.sort_values(by='_mag')
    fbs = fbs.drop_duplicates(subset=['_mjd', '_mag'], keep='last')
    if mag == 999: 
        fbs = fbs.head(10)        
    else:
        f2 = fbs[fbs.isfb]
        f1 = fbs[fbs['_mag'] < mag]
        fbs = pd.concat([f1, f2]).drop_duplicates()
    newm=pd.concat([fbs['url'],fbs['_mag'], fbs['_stream'], fbs['_vg'], fbs['mass'], fbs['_mjd'], fbs['orbname']], 
        axis=1, keys=['url','mag','shower','vg','mass','mjd', 'orbname'])
    return newm


# old version of the above for older data
def findFBPre2020(df, mag=-4):
    df=df[df._mag < mag]
    fbs=pd.concat([df._localtime,df._mag,df._stream,df._vg,df._a,df._e,df._incl,df._peri,df._node,df._p], axis=1, 
        keys=['url','mag','shower','vg','a','e','incl','peri','node','p'])
    fbs=fbs.sort_values(by=['mag','shower'])
    fbs['orbname']=['none' for i in fbs.mag]
    return fbs


def findFireballs (dtval, shwr, minmag=-3.99, matchdataset = None):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    orbdir = 'matches'

    # check if month was passed in
    mth = None
    if dtval > 9999:
        ym = dtval
        yr = int(str(ym)[:4])
        mth = int(str(ym)[4:6])
    else:
        yr = dtval

    if matchdataset is None:
        if yr > 2019:
            cols = ['_stream','_mjd','_mag','_vg','url','mass','orbname','_M_ut','isfb', '_Y_ut']
            filt = None
            fname = os.path.join(datadir, 'matched',f'matches-full-{yr}.parquet.snap')
            if os.path.isfile(fname):
                df = pd.read_parquet(fname, columns=cols, filters=filt)
                df = df[df['_Y_ut']==int(yr)] 
            else:
                print('unable to load datafile')
                exit(0)
        else:
            fname = os.path.join(datadir, 'matched',f'matches-{yr}.csv')
            if os.path.isfile(fname):
                df = pd.read_csv(fname, skipinitialspace=True)
            else:
                print('unable to load datafile')
                exit(0)
        # print('outdir is ', outdir)
        if shwr != 'ALL':
            df = df[df['_stream']==shwr]
        if mth is not None:
            df = df[df['_M_ut']==mth]

    else:
        df = matchdataset

    if minmag > 998:
        if mth is not None:
            outdir = os.path.join(datadir, 'reports',f'{yr:04d}', shwr, f'{mth:02d}')
        else:
            outdir = os.path.join(datadir, 'reports',f'{yr:04d}', shwr)
        orbdir = None
    else:
        outdir = os.path.join(datadir, 'reports',f'{yr}', 'fireballs')

    if yr > 2019:
        fbs = findMatchedFireballs(df, minmag)
    else:
        fbs = findFBPre2020(df, minmag)

    if len(fbs) > 0: 
        if outdir is not None:
            os.makedirs(outdir, exist_ok=True)
            outf = os.path.join(outdir, 'fblist.txt')
            fbs.to_csv(outf, index=False, header=False, columns=['url','mag','shower','orbname'])
        if shwr == 'ALL' and yr > 2019 and orbdir is not None:
            print('creating md files')
            createMDFiles(fbs, outdir, orbdir)


if __name__ == '__main__':
    dtval = int(sys.argv[1])
    shwr = sys.argv[2]
    if len(sys.argv) > 3:
        mag = float(sys.argv[3])
    else:
        mag = -3.9
    findFireballs(dtval, shwr, mag)
