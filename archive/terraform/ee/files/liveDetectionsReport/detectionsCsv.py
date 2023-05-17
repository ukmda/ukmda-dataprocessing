import boto3
import os
import datetime
import pandas as pd 
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddbjson


def prep_rawdata():
    sdt = datetime.datetime.now() + datetime.timedelta(days=-7)
    df = None
    hdr=['capturenight','timestamp','avg','brightness','sd','camera_id','image_URL']
    for i in range(0,7):
        thisdt = (sdt + datetime.timedelta(i)).strftime('%Y%m%d')
        print('processing', thisdt)
        df2 = pd.read_csv(f'CaptureNight_{thisdt}.csv', names=hdr)
        if df is None:
            df = df2
        else:
            df = pd.concat([df, df2])
    df['dtval'] = [datetime.datetime.fromtimestamp(d) for d in df.timestamp]
    df['duration'] = [0 for d in df.timestamp]
    df = df.drop(columns=['capturenight','avg','sd'])
    df['datetime'] = [datetime.datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%f') for d in df.dtval]
    df = df.sort_values(by=['dtval','camera_id'])
    df = df[['camera_id','datetime','brightness','duration','image_URL']]
    df.to_csv('ukmon-latest-v2.csv', index=False)



def getBrightnessData(yyyymmdd):
    sess = boto3.Session(profile_name='ukmonshared')
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    resp = table.query(KeyConditionExpression=Key('CaptureNight').eq(yyyymmdd))
    df = pd.DataFrame(ddbjson.loads(resp['Items']))
    if len(df) > 0:
        df = df.drop(columns=['CaptureNight','ExpiryDate','bstd','bave'])
        df['dtval'] = [datetime.datetime.fromtimestamp(d) for d in df.Timestamp]
        df['duration'] = [0 for d in df.Timestamp]
        df['datetime'] = [datetime.datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%f') for d in df.dtval]
        df = df.rename(columns={'camid':'camera_id', 'ffname': 'image_URL', 'bmax': 'brightness'})
        print(df)
        df = df[['camera_id','datetime','brightness','duration','image_URL']]
        df = df.sort_values(by=['datetime','camera_id'])
    return df


def updateDetectionsCsv():
    s3 = boto3.client('s3')
    srcbucket = os.getenv('SRCBUCKET', default='ukmeteornetworkarchive')
    csvname = os.getenv('CSVNAME', default='ukmon-latest-v2.csv')
    csvname = f'browse/daily/{csvname}'
    localf = '/tmp/ukmon-latest-v2.csv'
    s3.download_file(srcbucket, csvname, localf)
    df = pd.read_csv(localf)
    now = datetime.datetime.now()
    if now.hour < 13: 
        now = now + datetime.timedelta(days=-1)
    sdt = now + datetime.timedelta(days=-7)
    df = df[df.capturenight >= int(sdt.strftime('%Y%m%d'))]
    dtstr = int(now.strftime('%Y%m%d'))
    newrows = getBrightnessData(dtstr)
    if len(newrows) > 0:
        df = pd.concat([df, newrows])
    df = df.drop_duplicates(subset=['camera_id', 'datetime','brightness'])
    df.to_csv(localf, index=False)
    s3.upload_file(localf, srcbucket, csvname, ExtraArgs = {'ContentType': 'text/csv'})
    return 


def lambda_handler(event, context):
    updateDetectionsCsv()
