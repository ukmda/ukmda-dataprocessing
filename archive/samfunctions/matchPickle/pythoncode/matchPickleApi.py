# Copyright (C) 2018-2023 Mark McIntyre
import json
import os
import boto3
from wmpl.Utils.Pickling import loadPickle


def lambda_handler(event, context):
    try:
        archbucket = os.environ['ARCHBUCKET']
    except Exception:
        archbucket = 'mjmm-ukmonarchive.co.uk'

    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    reqval = qs['reqval']

    s3 = boto3.resource('s3')
    yr = reqval[:4]
    ym = reqval[:6]
    ymd = reqval[:8]
    pfname = reqval[:15]+'_trajectory.pickle'
    picklefile = f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{reqval}/{pfname}'
    try:
        print(f'{archbucket} {picklefile} {pfname}')
        s3.meta.client.download_file(archbucket, picklefile, f'/tmp/{pfname}')
        print('got file')
        p = loadPickle('/tmp', pfname)
        print('loaded pickle')
        pstr = p.toJson()
        print('converted to json string')
    except:
        pstr = '{"status" : "invalid trajectory"}'
    return {
        'statusCode': 200,
        'body': pstr #json.loads(pstr) 
    }
           
