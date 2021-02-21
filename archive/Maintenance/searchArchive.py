# python routine to search the S3 archive for specific criteria

import json
import boto3
import dateutil
import datetime
import os
import pytz
from operator import itemgetter


def FindMatch(bucket, csvfile, d1, d2):
    s3 = boto3.client('s3')

    ds1 = d1.timestamp()
    ds2 = d2.timestamp()

    expr = "SELECT * FROM s3object s where s.eventtime > '"+ f'{ds1}' + "' and s.eventtime < '" + f'{ds2}' +"'"
    utc=pytz.UTC
    comptime = utc.localize(datetime.datetime.today() + datetime.timedelta(days=-30))
    if d1 < comptime:
        expr = expr + " and s.source != 'Live' "
    print(expr)
    resp = s3.select_object_content(Bucket=bucket, Key=csvfile, ExpressionType='SQL',
        Expression=expr,
        InputSerialization={'CSV': {"FileHeaderInfo": "Use"}, 'CompressionType': 'NONE'},
        OutputSerialization={'CSV': {}},
    )
    res = []
    for event in resp['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            lines = records.split('\n')
            for r in lines:
                res.append(r)
    res.sort()
    res2 = []
    for r in res:
        s = r.split(',')
        if len(s) > 1: 
            res2.append([s[0], s[1], s[2], s[3], s[4], s[5], s[6]])
    res2 = sorted(res2, key=itemgetter(1,0))
    res =[]
    for rr in res2:
        res.append('{:s},{:s},{:s},{:s},{:s},{:s},{:s}'.format(rr[0], rr[1], rr[2], rr[3], rr[4], rr[5], rr[6]))
    return res


def lambda_handler(event, context):
    try:
        target = os.environ['SRCHBUCKET']
    except Exception:
        target = 'mjmm-ukmonarchive.co.uk'

    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    a = qs['a']
    b = qs['b']

    # a is of the form 2021-02-28T00:30:00.000Z
    if len(a) < len('2020-12-28T00:30:00.000Z'):
        res='invalid start date'
    elif len(b) < len('2021-02-28T00:30:00.000Z'):
        res='invalid end date'
    else:
        d1 = dateutil.parser.isoparse(a)
        d2 = dateutil.parser.isoparse(b)
        idxfile = 'search/indexes/{:04d}-allevents.csv'.format(d1.year)
        res = FindMatch(target, idxfile, d1, d2)

    print(res)
    return {
        'statusCode': 200,
        'body': "myFunc(" + json.dumps(res) + ")"
    }


def main():
    a = '2021-01-25T20:20:00.000Z'
    d1 = dateutil.parser.isoparse(a)
    d2 = d1 + datetime.timedelta(minutes=20)
    try:
        target = os.environ['SRCHBUCKET']
    except Exception:
        target = 'mjmm-ukmonarchive.co.uk'

    idxfile = 'search/indexes/{:04d}-allevents.csv'.format(d1.year)
    print(idxfile)
    res = FindMatch(target, idxfile, d1, d2)
    for li in res:
        print(li)


if __name__ == '__main__':
    main()
