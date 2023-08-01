# Copyright (C) 2018-2023 Mark McIntyre
import json
import os
import boto3

# need to include WMPL because the pickle file references structures in it
from wmpl.Utils.Pickling import loadPickle


def lambda_handler(event, context):
    archbucket = os.getenv('ARCHBUCKET', default= 'ukmon-shared')

    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    if 'reqval' in qs:
        reqval = qs['reqval']
    else:
        reqval = qs['orbit']
    if 'format' in qs:
        rettyp = qs['format']
    else:
        rettyp = 'json'

    s3 = boto3.client('s3', region_name='eu-west-2')
    yr = reqval[:4]
    ym = reqval[:6]
    ymd = reqval[:8]
    pfname = reqval[:15]+'_trajectory.pickle'
    picklefile = f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{reqval}/{pfname}'
    print(f'looking for {picklefile}')
    objlist = s3.list_objects_v2(Bucket=archbucket, Prefix=picklefile)
    if objlist['KeyCount'] > 0:
        k = objlist['Contents'][0]
        key = k['Key']
        if rettyp.lower() == 'json':
            print('returning json type')
            s3.download_file(archbucket, key, f'/tmp/{pfname}')
            p = loadPickle('/tmp', pfname)
            pstr = p.toJson()
        else:
            print('returning presigned url')
            url = s3.generate_presigned_url(ClientMethod='get_object', 
                                            Params={'Bucket': archbucket,'Key': key}, ExpiresIn=300)
            pstr = json.dumps({'filename': pfname, 'url': url})
    else:
        pstr = json.dumps({'status': 'invalid trajectory'})

    return {
        'statusCode': 200,
        'body': pstr
    }
