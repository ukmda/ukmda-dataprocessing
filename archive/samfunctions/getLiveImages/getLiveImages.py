#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
from boto3.dynamodb.conditions import Key
import json
import datetime


def getLiveImages(dtstr):
    ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('live')
    resp = table.query(IndexName='month-image_name-index', 
                       KeyConditionExpression=Key('month').eq(dtstr[4:6]) & Key('image_name').begins_with(f'M{dtstr}'),
                       ProjectionExpression='image_name')
    return resp


def getImageUrls(dtstr, statid, token=None, maxitems=100):
    s3 = boto3.client('s3')
    buckname = 'ukmda-live'
    if token is None:
        resp = s3.list_objects_v2(Bucket=buckname, MaxKeys = maxitems*2, Prefix=f'M{dtstr}')
    else:
        resp = s3.list_objects_v2(Bucket=buckname, MaxKeys = maxitems*2, ContinuationToken = token, Prefix=f'M{dtstr}')
    urls = []
    if resp['KeyCount'] > 0:
        for key in resp['Contents']:
            keyval = key['Key']
            if '.jpg' in keyval:
                psurl = s3.generate_presigned_url(ClientMethod='get_object',Params={'Bucket': buckname,'Key': keyval}, ExpiresIn=1800)
                urls.append({'url': f'{psurl}'})
        if 'NextContinuationToken' in resp:
            token = resp['NextContinuationToken']
    retval = {'pagetoken': token, 'urls': urls}
    return retval


def lambda_handler(event, context):
    #print(event)
    qs = event['queryStringParameters']
    if 'pattern' in qs:
        patt = qs['pattern']
        print(f'searching for {patt}')
        ecsvstr = getLiveImages(patt)
        print(f"found {ecsvstr['Items']}")
        return {
            'statusCode': 200,
            'body': json.dumps(ecsvstr['Items'])
        }
    else:
        maxitems = 100
        if 'dtstr' in qs:
            dtstr = qs['dtstr'] 
        else:
            dtstr = datetime.datetime.now().strftime('M%Y%m%d_%H')
        statid = None
        if 'statid' in qs:
            statid = qs['statid']
        conttoken = None
        if 'conttoken' in qs:
            conttoken = qs['conttoken']
        print(dtstr, statid, maxitems)
        retval = getImageUrls(dtstr, statid, conttoken, maxitems)
        return {
            'statusCode': 200,
            'body': "showImages(" + json.dumps(retval) + ")"
        }
