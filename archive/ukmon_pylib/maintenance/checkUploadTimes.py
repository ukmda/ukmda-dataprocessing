import os
import boto3
import pandas as pd
import datetime

from reports.CameraDetails import loadLocationDetails, findSite, findEmail


def findLatestFTPs(dtstr='20230813', archbucket='ukmda-shared'):
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


def ftpsAfterBatchStart(batchtime=None, archbucket='ukmda-shared'):
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
    camdets = loadLocationDetails(ddb=ddb)
    lateftps['location'] = [findSite(c, camdets) for c in lateftps.camid]
    lateftps['owner'] = [findEmail(c, camdets) for c in lateftps.camid]
    lateftps = lateftps.sort_values(by=['owner','camid'])
    lateftps.to_csv(os.path.join(datadir, 'lateftps.csv'), index=True)
    return lateftps


if __name__ == '__main__':
    testdt = datetime.datetime.now()
    testdt = datetime.datetime(testdt.year, testdt.month, testdt.day, 2, 0, 0)
    ftpsAfterBatchStart(testdt)
