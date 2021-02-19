# python routine to search the S3 archive for specific criteria

import json
import boto3
import dateutil
import os


def FindMatch(bucket, csvfile, d1, d2):
    s3 = boto3.client('s3')

    ds1 = d1.timestamp()
    ds2 = d2.timestamp()

    expr = "SELECT * FROM s3object s where s.eventtime > '"+ f'{ds1}' + "' and s.eventtime < '" + f'{ds2}' +"'"
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
    print(res)
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
    if len(a) < len('2021-02-28T00:30:00.000Z'):
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
    a = '2021-02-16T21:30:00.000Z'
    b = '2021-02-16T23:00:00.000Z'
    d1 = dateutil.parser.isoparse(a)
    d2 = dateutil.parser.isoparse(b)
    try:
        target = os.environ['SRCHBUCKET']
    except Exception:
        target = 'mjmm-ukmonarchive.co.uk'

    idxfile = 'search/indexes/{:04d}-allevents.csv'.format(d1.year)
    print(idxfile)
    res = FindMatch(target, idxfile, d1, d2)
    print(res)


if __name__ == '__main__':
    main()
