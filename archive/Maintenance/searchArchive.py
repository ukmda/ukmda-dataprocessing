# python routine to search the S3 archive for specific criteria

import json
import boto3
# import uuid
# import os


def FindMatch(bucket, csvfile, yr, mth, dy, hr, mn, yr2, mth2, dy2, hr2, mn2):
    s3 = boto3.client('s3')

    resp = s3.select_object_content(
        Bucket=bucket,
        Key=csvfile,
        ExpressionType='SQL',
        Expression="SELECT * FROM s3object s where " +
        "s.\"Y(UT)\" like '" + f'{yr:04}' + "' and s.\"M(UT)\" like '" + f'{mth:02}' + "' " +
        "and  s.\"D(UT)\" like '" + f'{dy:02}' + "' " +
        "and s.\"H(UT)\" like '" + f'{hr:02}' + "' and s.\"M\" like '" + f'{mn:02}' + "'",
        InputSerialization={'CSV': {"FileHeaderInfo": "Use"}, 'CompressionType': 'NONE'},
        OutputSerialization={'CSV': {}},
    )
    res = []
    for event in resp['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            flds = records.split(',')
            res.append(flds[2] + ',' + flds[1] + ',' + flds[6] + ',' + flds[4])
    return res
    

def FindLiveMatch(bucket, csvfile, yr, mth, dy, hr, mn, yr2, mth2, dy2, hr2, mn2):
    s3 = boto3.client('s3')

    ymd = f'{yr:04}{mth:02}{dy:02}'
    hms = f'{hr:02}{mn:02}%'
    resp = s3.select_object_content(
        Bucket=bucket,
        Key=csvfile,
        ExpressionType='SQL',
        Expression="SELECT * FROM s3object s where " +
        "_1 like '" + ymd + "' and _2 like '" + hms + "'",
        InputSerialization={'CSV': {}, 'CompressionType': 'NONE'},
        OutputSerialization={'CSV': {}},
    )
    res = []
    for event in resp['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            flds = records.split(',')
            flds = records.split(',')
            res.append(flds[0] + '_' + flds[1] + ',' + '-' + ',' + flds[2] + '_' + flds[3] +',-')
    return res
    

def lambda_handler(event, context):
    # conn = boto3.client('s3')
    # s3 = boto3.resource('s3')
    # target = 'ukmon-shared'
    
    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    a = qs['a']
    b = qs['b']

    # a is of the form 2021-02-28T00:30:00.000Z
    if len(a) < len('2021-02-28T00:30:00.000Z'):
        res='invalid start date'
    elif len(b) < len('2021-02-28T00:30:00.000Z'):
        res='invalid end date'
    else:
        yr=int(a[:4])
        mth=int(a[5:7])
        dy=int(a[8:10])
        hr=int(a[11:13])
        mi=int(a[14:16])
        yr2=int(b[:4])
        mth2=int(b[5:7])
        dy2=int(b[8:10])
        hr2=int(b[11:13])
        mi2=int(b[14:16])
        if mth < 4:
            qtr='01'
        elif mth < 7:
            qtr='02'
        elif mth < 10:
            qtr='03'
        else:
            qtr='04'
        res1 = FindMatch("ukmon-shared", "consolidated/M_{:04d}-unified.csv".format(yr), yr, mth, dy, hr, mi, yr2, mth2, dy2, hr2, mi2)
        res2 = FindLiveMatch("ukmon-live", "idx{:04d}{:s}.csv".format(yr, qtr), yr, mth, dy, hr, mi, yr2, mth2, dy2, hr2, mi2)
        res = res1 + res2
        

    print(res)
    return {
        'statusCode': 200,
        'body': "myFunc(" + json.dumps(res) + ")"
    }


def main():
    a = '2021-02-16T21:30:00.000Z'
    b = '2021-02-16T23:00:00.000Z'
    yr=int(a[:4])
    mth=int(a[5:7])
    dy=int(a[8:10])
    hr=int(a[11:13])
    mi=int(a[14:16])
    yr2=int(b[:4])
    mth2=int(b[5:7])
    dy2=int(b[8:10])
    hr2=int(b[11:13])
    mi2=int(b[14:16])
    if mth < 4:
        qtr='01'
    elif mth < 7:
        qtr='02'
    elif mth < 10:
        qtr='03'
    else:
        qtr='04'

    res1 = FindMatch("ukmon-shared", "consolidated/M_{:04d}-unified.csv".format(yr), yr, mth, dy, hr, mi, yr2, mth2, dy2, hr2, mi2)
    res2 = FindLiveMatch("ukmon-live", "idx{:04d}{:s}.csv".format(yr, qtr), yr, mth, dy, hr, mi, yr2, mth2, dy2, hr2, mi2)
    res = res1 + res2
    print(res)


if __name__ == '__main__':
    main()
