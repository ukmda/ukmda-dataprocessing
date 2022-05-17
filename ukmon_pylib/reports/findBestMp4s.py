import pandas as pd
import boto3
import shutil
import sys
import os
from traj.pickleAnalyser import getAllMp4s


def getBestNMp4s(yr, mth, numtoget):
    datadir=os.getenv('DATADIR')
    mf = os.path.join(datadir, 'matched', f'matches-full-{yr}.parquet.gzip')
    matches = pd.read_parquet(mf)
    matches = matches[matches._Y_ut == int(yr)]
    matches = matches[matches._M_ut == int(mth)]
    sepdata = matches.sort_values(by=['_mag'])
    sorteddata = sepdata.head(numtoget)

    tmpdir = os.getenv('TMP')
    wsbucket = os.getenv('UKMONSHAREDBUCKET')[5:]
    s3 = boto3.resource('s3')
    mp4df = pd.DataFrame()
    for traj in sorteddata.url:
        trdir = traj[traj.find('reports'):]
        spls = trdir.split('/')
        trdir = f'matches/RMSCorrelate/trajectories/{spls[1]}/{spls[3]}/{spls[4]}/{spls[5]}'
        trname = spls[5]
        picklefile = trname[:15] + '_trajectory.pickle'
        key = trdir + '/' + picklefile
        locdir = os.path.join(tmpdir, trname)
        os.makedirs(locdir, exist_ok=True)
        key = trdir + '/' + picklefile
        picklename = os.path.join(locdir, picklefile)
        s3.meta.client.download_file(wsbucket, key, picklename)
        key = trdir + '/mpgs.lst'
        locfname = os.path.join(locdir, 'mpgs.lst')
        try:
            s3.meta.client.download_file(wsbucket, key, locfname) # used by getAllMP4s
            newdf = getAllMp4s(picklename)
            mp4df = pd.concat([mp4df, newdf])
        except:
            pass
        shutil.rmtree(locdir)

    if len(mp4df) > 0:
        mp4df = mp4df.drop_duplicates()
        print(mp4df)
        mp4df = mp4df.sort_values(by=['mag']).head(numtoget)
        return list(mp4df.mp4)
    else:
        return []


if __name__ == '__main__':
    lst = getBestNMp4s(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    for li in lst:
        print(li)
