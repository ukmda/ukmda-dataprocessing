# Copyright (C) 2018-2023 Mark McIntyre
import json
import datetime
import os
import boto3


def lambda_handler(event, context):
    target = os.getenv('SRCHBUCKET', default='ukmda-shared')
    #print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    if qs is None:
        return {
            'statusCode': 200,
            'body': 'usage: detections?reqtyp=xxx&reqval=yyyy'
        }
    reqtyp = qs['reqtyp']
    reqval = qs['reqval']

    if reqtyp not in ['matches','detail','station']:
        res = '{"invalid request type - must be one of \'matches\', \'details\' or \'station\'"}'
    else:
        if reqtyp == 'matches':
            d1 = datetime.datetime.strptime(reqval, '%Y%m%d')
            idxfile = 'matches/matched/matches-full-{:04d}.csv'.format(d1.year)
            res = '{"no matches"}'
            expr = "SELECT s.orbname from s3object s where s._localtime like '_{}%'".format(reqval)
            fhi = {"FileHeaderInfo": "Use"}
        if reqtyp == 'detail':
            idxfile = 'matches/matched/matches-full-{}.csv'.format(reqval[:4])
            res = '{"event not found"}'
            expr = "SELECT * from s3object s where s.orbname='{}'".format(reqval)
            fhi = {"FileHeaderInfo": "Use"}
        if reqtyp == 'station':
            statid = qs['statid']
            d1 = datetime.datetime.strptime(reqval, '%Y%m%d')
            idxfile = 'matches/matched/matches-full-{:04d}.csv'.format(d1.year)
            res = '{"no matches"}'
            expr = "SELECT s.orbname from s3object s where s._localtime like '_{}%' and s.stations like '%{}%'".format(reqval, statid)
            fhi = {"FileHeaderInfo": "Use"}

        s3 = boto3.client('s3')
        resp = s3.select_object_content(Bucket=target, Key=idxfile, ExpressionType='SQL',
            Expression=expr, InputSerialization={'CSV': fhi, 'CompressionType': 'NONE'}, OutputSerialization={'JSON': {}}, )
        res=''
        for event in resp['Payload']:
            if 'Records' in event:
                res = res + event['Records']['Payload'].decode('utf-8')
    
    return {
        'statusCode': 200,
        'body': res # json.dumps(res)
    }
