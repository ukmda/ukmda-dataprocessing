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


def filterImages(d1, d2, statid=None, maxitems=-1):
    ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('live')
    if maxitems == -1:
        lv=f'{d1.timestamp()*1000:.0f}'
        hv=f'{d2.timestamp()*1000:.0f}'
        resp = table.query(IndexName='year-image_timestamp-index', 
                            KeyConditionExpression=Key('year').eq(str(d1.year)) & Key('image_timestamp').between(lv, hv),
                            ProjectionExpression='image_name',
                            ScanIndexForward = False)
    else:
        resp = table.query(IndexName='year-image_timestamp-index', 
                            KeyConditionExpression=Key('year').eq(str(d1.year)),
                            Limit=maxitems,
                            ProjectionExpression='image_name',
                            ScanIndexForward = False)
    if statid is not None:
        imglist = [x['image_name'] for x in resp['Items'] if statid in x['image_name']]
    else:
        imglist = [x['image_name'] for x in resp['Items']]
    return imglist


def getImageUrls(dtstr, dtstr2, statid, token=None, maxitems=100, includexml=False):
    s3 = boto3.client('s3')
    buckname = 'ukmda-live'
    if dtstr == 'latest':
        enddt = datetime.datetime.now()
        enddt = enddt.replace(hour=8, minute=9)
        startdt = enddt + datetime.timedelta(hours=-2)
    else:
        startdt = datetime.datetime.strptime(dtstr, '%Y-%m-%dT%H:%M:%S.000Z')
        enddt = datetime.datetime.strptime(dtstr2, '%Y-%m-%dT%H:%M:%S.000Z')
        maxitems = -1
    imglist = filterImages(startdt, enddt, statid, maxitems)

    urls = []
    for keyval in imglist:
        if '.jpg' in keyval:
            print(statid, keyval)
            psurl = s3.generate_presigned_url(ClientMethod='get_object',Params={'Bucket': buckname,'Key': keyval}, ExpiresIn=1800)
            urls.append({'url': f'{psurl}'})
            if includexml:
                xmlkey = keyval.replace('P.jpg', '.xml')
                psurl = s3.generate_presigned_url(ClientMethod='get_object',Params={'Bucket': buckname,'Key': xmlkey}, ExpiresIn=1800)
                urls.append({'url': f'{psurl}'})
                
    urls.sort(key = lambda k: k['url'], reverse=True)
    urls = urls[:maxitems]
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
            dtstr = 'latest'
        if 'enddtstr' in qs:
            dtstr2 = qs['enddtstr'] 
        else:
            dtstr2 = datetime.datetime.now().strftime('M%Y%m%d_%H')
        statid = None
        if 'statid' in qs:
            statid = qs['statid']
        fmt = None
        incxml = False
        if 'fmt' in qs:
            fmt = qs['fmt']
            if fmt == 'withxml':
                incxml = True
                fmt = 'json'
        conttoken = None
        if 'conttoken' in qs:
            conttoken = qs['conttoken']
        print(dtstr, dtstr2, statid, maxitems)
        retval = getImageUrls(dtstr, dtstr2, statid, conttoken, maxitems, includexml=incxml)
        if fmt == 'json':
            return {
                'statusCode': 200,
                'body': json.dumps(retval)
            }
        else:
            return {
                'statusCode': 200,
                'body': "showImages(" + json.dumps(retval) + ")"
            }
