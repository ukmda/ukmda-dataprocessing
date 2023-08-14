import os
import boto3
import pandas as pd
import datetime
from boto3.dynamodb.conditions import Key


def findSite(stationid, tbl):
    response = tbl.query(KeyConditionExpression=Key('stationid').eq(stationid))
    try:
        items = response['Items']
        if len(items) > 0:
            return items[0]['site']
        else:
            return 'unknown'
    except Exception:
        print('record not found')
    return None


def findEmail(stationid, camdets):
    cc = camdets[camdets.camid==stationid]
    if len(cc) > 0:
        res = cc.iloc[0]['eMail']
    else:
        res = 'Unknown'
    return res


def findLatestFTPs(dtstr='20230813', archbucket='ukmon-shared'):
    s3 = boto3.resource('s3')
    location='matches/RMSCorrelate/UK'
    bucket = s3.Bucket(archbucket)
    files=[fl.key for fl in bucket.objects.filter(Prefix=location)]
    fltfiles=[file for file in files if '.txt' in file and dtstr in file]
    ftptimes = []
    for f in fltfiles:
        resp = s3.meta.client.head_object(Bucket=archbucket, Key=f)
        _, fn = os.path.split(f)
        ftptimes.append([fn, resp['LastModified']])
    df = pd.DataFrame(ftptimes, columns=['name','uploadtime'])
    df.sort_values(by=['uploadtime'])
    df = df.set_index(['uploadtime'])
    return df


def ftpsAfterBatchStart(batchtime=None, archbucket='ukmon-shared'):
    if batchtime is None:
        batchtime=pd.Timestamp(datetime.datetime.now(), tz='UTC')
    else:
        batchtime=pd.Timestamp(batchtime, tz='UTC')
    reqdate = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    ftps = findLatestFTPs(reqdate, archbucket)
    lateftps =ftps[ftps.index > batchtime]
    lateftps['camid'] = [f[14:20] for f in lateftps.name]
    lateftps = lateftps.drop(columns=['name'])
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    sess = boto3.Session(profile_name='ukmonshared')
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    tbl = ddb.Table('camdetails')
    lateftps['location'] = [findSite(c,tbl) for c in lateftps.camid]
    camdets = pd.read_csv(os.path.join(datadir, 'admin','stationdetails.csv'))
    lateftps['owner'] = [findEmail(c,camdets) for c in lateftps.camid]
    lateftps = lateftps.sort_values(by=['owner','camid'])
    lateftps.to_csv(os.path.join(datadir, 'lateftps.csv'), index=True)
    return lateftps


if __name__ == '__main__':
    testdt = datetime.datetime.now()
    testdt = datetime.datetime(testdt.year, testdt.month, testdt.day, 2, 0, 0)
    ftpsAfterBatchStart(testdt)
