# comparing Brightness data with RMS-calculated magnitudes

import os
import sys
import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddbjson
import pandas as pd
import datetime


def getBrightnessData(yyyymmdd, outdir=None):
    prof = os.getenv('UKMPROFILE',default='ukmonshared')
    sess = boto3.Session(profile_name=prof)
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    resp = table.query(KeyConditionExpression=Key('CaptureNight').eq(yyyymmdd))
    df = pd.DataFrame(ddbjson.loads(resp['Items']))
    if outdir is not None:
        with open(os.path.join(outdir, f'CaptureNight_{yyyymmdd}.csv'), 'w') as outf:
            for i in resp['Items']:
                outf.write(f"{i['CaptureNight']},{i['Timestamp']},{i['bmax']},{i['bave']},{i['bstd']},{i['camid']},")
                if 'ffname' in i:
                    outf.write(f"{i['ffname']}\n")
                else:
                    outf.write('\n')
    return df


def getMagData(yyyymmdd):
    url = f'https://archive.ukmeteors.co.uk/browse/parquet/singles-{str(yyyymmdd)[:4]}.parquet.snap'
    df = pd.read_parquet(url, columns=['Filename', 'Dtstamp', 'Mag'])
    # filter by day
    d1 = datetime.datetime.strptime(str(yyyymmdd), '%Y%m%d') + datetime.timedelta(hours=12)
    d2 = datetime.datetime.strptime(str(yyyymmdd), '%Y%m%d') + datetime.timedelta(hours=36)
    df = df[df.Dtstamp > d1.timestamp()]
    df = df[df.Dtstamp < d2.timestamp()]
    df = df.rename(columns={'Filename': 'ffname'})
    return df


def getMatchedData(yyyymmdd, outdir=None):
    if outdir is None:
        outdir = 'E:/dev/meteorhunting/testing/brightness_tests'
    bri = getBrightnessData(yyyymmdd, outdir)
    mag = getMagData(yyyymmdd)
    mag = mag.rename(columns={'Filename': 'ffname'})
    if len(bri) > 0:
        comb = bri.merge(mag, on='ffname', how='outer')
        comb = comb[comb.CaptureNight.notnull()]
        comb['sds'] = (comb.bmax-comb.bave)/comb.bstd
        comb.to_csv(os.path.join(outdir, f'matcheddata-{yyyymmdd}.csv'))
    else:
        print('no brightness data available')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        dtval = int((datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d'))
    else:
        dtval = int(sys.argv[1])
    if len(sys.argv) < 3:
        outdir='.'
    else:
        outdir=sys.argv[2]
    print(dtval, outdir)
    getMatchedData(dtval, outdir)
