# Copyright (C) 2018-2023 Mark McIntyre

# manage the trajectory database
import os
import pandas as pd
import boto3


# delete an orbit from the database
def deleteDuplicate(trajname, jd=None):
    datadir = os.getenv('DATADIR', default='/home/pi/prod/data')
    yr=trajname[:4]
    if int(yr) > 2021:
        fname = os.path.join(datadir, 'matched','matches-full-{}.parquet.snap'.format(yr))
        if os.path.isfile(fname):
            # cant select columns as we are going to write the whole lot back out
            df = pd.read_parquet(fname)
        else:
            print('unable to load datafile')
            return 0
    else:
        print("can only be done for 2022 onwards")
        return 0
    seldf = df[df.orbname==trajname]
    idx = seldf.index
    if jd:
        idx = seldf[seldf._mjd == jd].index
    if len(idx) == 1:
        df = df.drop(index=idx)
        df.to_parquet(fname, compression='snappy')
        csvfname = os.path.join(datadir, 'matched','matches-full-{}.csv'.format(yr))
        df.to_csv(csvfname, index=False)
        if jd is None:
            deleteWebPage(trajname)
        return 0
    elif len(idx) > 1:
        print(f'two or more matches to {trajname}, please select MJD')
        for _,rw in seldf.iterrows():
            print(f'{rw._mjd}, {rw.orbname}, {rw._amag}, {rw._stream}')
        return 1
    else:
        print(f'no match for {trajname}')
        return 1


def deleteWebPage(trajname):
    webbucket = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')[5:]
    yr = trajname[:4]
    ym = trajname[:6]
    ymd = trajname[:8]
    fldrname = f'reports/{yr}/orbits/{ym}/{ymd}/{trajname}'
    print(f'webpath = {webbucket}/{fldrname}')
    s3 = boto3.resource('s3')
    objects_to_delete = s3.meta.client.list_objects(Bucket=webbucket, Prefix=fldrname)
    delete_keys = {'Objects': []}
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
    #print(delete_keys)
    s3.meta.client.delete_objects(Bucket=webbucket, Delete=delete_keys)
    return
