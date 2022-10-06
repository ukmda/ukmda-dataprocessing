# manage the trajectory database
import os
import pandas as pd
import boto3


# delete an orbit from the database
def deleteDuplicate(trajname):
    datadir = os.getenv('DATADIR', default='/home/pi/prod/data')
    yr=trajname[:4]
    if int(yr) > 2021:
        fname = os.path.join(datadir, 'matched','matches-full-{}.parquet.gzip'.format(yr))
        if os.path.isfile(fname):
            df = pd.read_parquet(fname)
        else:
            print('unable to load datafile')
            return 0
    else:
        print("can only be done for 2022 onwards")
        return 0
    idx = df[df.orbname==trajname].index
    if len(idx) > 0:
        df = df.drop(index=idx)
        df.to_parquet(fname)
        csvfname = os.path.join(datadir, 'matched','matches-full-{}.csv'.format(yr))
        df.to_csv(csvfname, index=False)

        deleteWebPage(trajname)
        return 1
    else:
        print(f'no match for {trajname}')
        return 0


def deleteWebPage(trajname):
    webbucket = os.getenv('WEBSITEBUCKET', default='s3://ukmeteornetworkarchive')
    webbucket = webbucket[5:]
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
