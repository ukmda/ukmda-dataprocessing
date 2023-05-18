import boto3
import os
import datetime
import pandas as pd 
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddbjson


def _getUkmonIDFromGMNId(camid, camdets):
    mtchs = [cam for cam in camdets if camid in cam]
    if len(mtchs) == 0:
        return 'Unknown'
    for li in mtchs:
        spls = li.split(',')
        active = int(spls[-1].strip())
        if active == 1:
            return (spls[0] + '_' + spls[3]).lower()
    return 'Unknown'


def _prep_rawdata():
    sdt = datetime.datetime.now() + datetime.timedelta(days=-7)
    df = None
    hdr=['CaptureNight','Timestamp','avg','brightness','sd','camera_id','image_URL']
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


def getBrightnessData(yyyymmdd, camdets):
    #sess = boto3.Session(profile_name='ukmonshared')
    ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    resp = table.query(KeyConditionExpression=Key('CaptureNight').eq(yyyymmdd))
    df = pd.DataFrame(ddbjson.loads(resp['Items']))
    if len(df) > 0:
        df = df.drop(columns=['CaptureNight','ExpiryDate','bstd','bave'])
        df['dtval'] = [datetime.datetime.fromtimestamp(d) for d in df.Timestamp]
        df['duration'] = [0 for d in df.Timestamp]
        df['datetime'] = [datetime.datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%f') for d in df.dtval]
        df['dtstr'] = [datetime.datetime.strftime(d, '%Y%m%d_%H%M%S') for d in df.dtval]
        df['ukmonid'] = [_getUkmonIDFromGMNId(camera, camdets) for camera in df.camid]
        df['image_URL']='https://live.ukmeteornetwork.co.uk/M'+df.dtstr + '_' + df.ukmonid + '_' + df.camid + 'P.jpg'
        df = df.rename(columns={'camid':'camera_id', 'bmax': 'brightness'})
        print(df)
        df = df[['camera_id','datetime','brightness','duration','image_URL']]
        df = df.sort_values(by=['datetime','camera_id'])
    return df


def updateDetectionsCsv():
    s3 = boto3.client('s3', region_name='eu-west-2')
    tmpdir = os.getenv('TMP', default='/tmp')
    localf = os.path.join(tmpdir, 'camera-details.csv')
    s3.download_file('ukmon-shared', 'consolidated/camera-details.csv', localf)
    camdets = open(localf, 'r').readlines()
    os.remove(localf)

    s3 = boto3.client('s3')
    srcbucket = os.getenv('SRCBUCKET', default='ukmeteornetworkarchive')
    csvname = os.getenv('CSVNAME', default='ukmon-latest-v2.csv')
    csvname = f'browse/daily/{csvname}'
    tmpdir = os.getenv('TEMP', default='/tmp')
    localf = os.path.join(tmpdir, 'ukmon-latest-v2.csv')
    try:
        s3.download_file(srcbucket, csvname, localf)
        df = pd.read_csv(localf)
        print('got existing file')
        df['dtval'] = pd.to_datetime(df.datetime)
        df['dtstr'] = [datetime.datetime.strftime(d, '%Y%m%d_%H%M%S') for d in df.dtval]
        df['ukmonid'] = [_getUkmonIDFromGMNId(camera, camdets) for camera in df.camera_id]
        df['image_URL']='https://live.ukmeteornetwork.co.uk/M'+df.dtstr + '_' + df.ukmonid + '_' + df.camera_id + 'P.jpg'
        df = df.drop(columns=['dtval','dtstr','ukmonid'])
    except:
        df = None
    now = datetime.datetime.now()
    if now.hour < 13: 
        now = now + datetime.timedelta(days=-1)
    dtstr = int(now.strftime('%Y%m%d'))
    newrows = getBrightnessData(dtstr, camdets)
    if len(newrows) > 0:
        print('got some data')
        if df is not None:
            print('concatenate data')
            df = pd.concat([df, newrows])
        else:
            print('no existing data')
            df = newrows
    sdt = now + datetime.timedelta(days=-7)
    print(df)

    df = df[pd.to_datetime(df.datetime) > sdt]
    df = df.drop_duplicates(subset=['camera_id', 'datetime','brightness'])
    df.to_csv(localf, index=False)
    s3.upload_file(localf, srcbucket, csvname, ExtraArgs = {'ContentType': 'text/csv'})
    return 


def lambda_handler(event, context):
    updateDetectionsCsv()


def test_createDetectionsCSV():
    updateDetectionsCsv()
    assert 1==1
