# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
import boto3
import shutil
import sys
import os
import datetime
import requests
from traj.pickleAnalyser import getAllMp4s


def getBestNMatches(reqdate=None, numtoget=10):
    if reqdate is None:
        tod = datetime.datetime.now()
        tod = tod.replace(hour=12, minute=0, second=0, microsecond=0)
        reqdate = tod + datetime.timedelta(days=-1)
    else:
        reqdate = reqdate.replace(hour=12, minute=0, second=0, microsecond=0)
        tod = reqdate + datetime.timedelta(days=1)

    yr = reqdate.year
    datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    mf = os.path.join(datadir, 'matched', f'matches-full-{yr}.parquet.snap')

    # select only the columns we need
    cols=['_localtime', '_mag','url']
    matches = pd.read_parquet(mf, columns=cols)
    matches['dt'] = [datetime.datetime.strptime(x,'_%Y%m%d_%H%M%S') for x in matches._localtime]    

    matches = matches[matches.dt >= reqdate]
    matches = matches[matches.dt <= tod]
    sepdata = matches.sort_values(by=['_mag'])
    sorteddata = sepdata.head(numtoget)
    sorteddata.drop_columns(['_localtime'], inplace=True)


def getBestNSingles(reqdate=None, numtoget=20, shwr=None, outdir=None):
    if reqdate is None:
        tod = datetime.datetime.now()
        tod = tod.replace(hour=12, minute=0, second=0, microsecond=0)
        reqdate = tod + datetime.timedelta(days=-1)
    else:
        print(reqdate)
        reqdate = datetime.datetime.strptime(reqdate, '%Y%m%d')
        reqdate = reqdate.replace(hour=12, minute=0, second=0, microsecond=0)
        tod = reqdate + datetime.timedelta(days=1)
    yr = reqdate.year
    url = f'https://archive.ukmeteors.co.uk/browse/parquet/singles-{yr}.parquet.snap'

    # select only the columns we need
    cols=['Mag','Shwr','Filename','Dtstamp']
    matches = pd.read_parquet(url, columns=cols)

    matches = matches[matches.Dtstamp >= reqdate.timestamp()]
    matches = matches[matches.Dtstamp <= tod.timestamp()]
    sepdata = matches.sort_values(by=['Mag'])
    sepdata['url'] = [getUrlFromFilename(x) for x in sepdata.Filename]
    if shwr:
        sepdata = sepdata[sepdata.Shwr==shwr]
    sorteddata = sepdata.head(numtoget)
    if outdir:
        outdir = os.path.join(outdir, reqdate.strftime('%Y%m%d'))
        os.makedirs(outdir, exist_ok=True)
        for _, rw in sorteddata.iterrows():
            fname = (f'{rw.Shwr}_{rw.Mag}_{rw.Filename}').replace('.fits','.jpg')
            print(fname)
            res = requests.get(rw.url)
            if res.status_code == 200:
                open(os.path.join(outdir, fname),'wb').write(res.content)

    filtereddata = sorteddata.drop(columns=['Dtstamp','Filename'])
    return filtereddata


def getUrlFromFilename(fname):
    ymd = fname.split('_')[2]
    jpgname = fname.replace('.fits','.jpg')
    url = f'https://archive.ukmeteors.co.uk/img/single/{ymd[:4]}/{ymd[:6]}/{jpgname}'
    return url


def getBestNMp4s(yr, mth, numtoget):
    datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    mf = os.path.join(datadir, 'matched', f'matches-full-{yr}.parquet.snap')

    # select only the columns we need
    cols=['_Y_ut','_M_ut','_mag','url']
    matches = pd.read_parquet(mf, columns=cols)

    matches = matches[matches._Y_ut == int(yr)]
    matches = matches[matches._M_ut == int(mth)]
    sepdata = matches.sort_values(by=['_mag'])
    sorteddata = sepdata.head(numtoget)

    tmpdir = os.getenv('TMP', default='/tmp')
    wsbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
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
        try: 
            s3.meta.client.download_file(wsbucket, key, picklename)
            key = trdir + '/mpgs.lst'
            locfname = os.path.join(locdir, 'mpgs.lst')
            try:
                s3.meta.client.download_file(wsbucket, key, locfname) # used by getAllMP4s
                newdf = getAllMp4s(picklename)
                mp4df = pd.concat([mp4df, newdf])
            except:
                pass
        except:
            pass
        shutil.rmtree(locdir)

    if len(mp4df) > 0:
        mp4df = mp4df.drop_duplicates()
        mp4df = mp4df.sort_values(by=['mag']).head(numtoget)
        return list(mp4df.mp4)
    else:
        return []


if __name__ == '__main__':
    lst = getBestNMp4s(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    for li in lst:
        print(li)
