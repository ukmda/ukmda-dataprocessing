#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
from boto3.dynamodb.conditions import Key
import json
import datetime
from decimal import Decimal


def getLiveImages(dtstr, ddb=None):
    if ddb is None:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('live')
    resp = table.query(IndexName='month-image_name-index', 
                        KeyConditionExpression=Key('month').eq(dtstr[4:6]) & Key('image_name').begins_with(f'M{dtstr}'),
                        ProjectionExpression='image_name')
    return resp


def filterImages(d1, d2, statid=None, maxitems=-1, ddb=None):
    if ddb is None:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('live')
    # print(maxitems, d1, d2)
    if maxitems == -1 or isinstance(d1, datetime.datetime):
        lv=f'{d1.timestamp()*1000:.0f}'
        hv=f'{d2.timestamp()*1000:.0f}'
        resp = table.query(IndexName='year-image_timestamp-index', 
                            KeyConditionExpression=Key('year').eq(str(d1.year)) & Key('image_timestamp').between(lv, hv),
                            ProjectionExpression='image_name',
                            ScanIndexForward = False)
    else:
        resp = table.query(IndexName='year-image_timestamp-index', 
                            KeyConditionExpression=Key('year').eq(str(d2.year)),
                            Limit=maxitems,
                            ProjectionExpression='image_name',
                            ScanIndexForward = False)
    if statid is not None:
        imglist = [x['image_name'] for x in resp['Items'] if statid in x['image_name']]
    else:
        imglist = [x['image_name'] for x in resp['Items']]
    return imglist


def getTrueImgs(dtstr, dtstr2, statid, ddb=None):
    if ddb is None:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    d1 = datetime.datetime.strptime(dtstr, '%Y-%m-%dT%H:%M:%S.000Z')
    d2 = datetime.datetime.strptime(dtstr2, '%Y-%m-%dT%H:%M:%S.000Z')
    if d1.hour < 13:
        capnight=(d1 + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    else:
        capnight = dtstr[:8]
    lv=Decimal(f'{d1.timestamp():.0f}')
    hv=Decimal(f'{d2.timestamp():.0f}')
    resp = table.query(KeyConditionExpression=Key('CaptureNight').eq(int(capnight)) & Key('Timestamp').between(lv, hv),
                        ProjectionExpression='ffname',
                        ScanIndexForward = False)
    if statid is not None:
        imglist = [x['ffname'] for x in resp['Items'] if statid in x['ffname']]
    else:
        imglist = [x['ffname'] for x in resp['Items']]
    return {'images': imglist}


def getImageUrls(dtstr, dtstr2, statid, token=None, maxitems=100, includexml=False, ddb=None):
    if ddb is None:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    s3 = boto3.client('s3')
    buckname = 'ukmda-live'
    if dtstr == 'latest':
        enddt = datetime.datetime.now()
        startdt = 'latest'
    else:
        startdt = datetime.datetime.strptime(dtstr, '%Y-%m-%dT%H:%M:%S.000Z')
        enddt = datetime.datetime.strptime(dtstr2, '%Y-%m-%dT%H:%M:%S.000Z')
        maxitems = -1
    imglist = filterImages(startdt, enddt, statid, maxitems, ddb)
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
    if maxitems > 0:
        urls = urls[:maxitems+1]
    retval = {'pagetoken': token, 'urls': urls}
    return retval


def lambda_handler(event, context):
    ddb = None
    qs = event['queryStringParameters']
    if 'pattern' in qs:
        patt = qs['pattern']
        print(f'searching for {patt}')
        ecsvstr = getLiveImages(patt, ddb=ddb)
        print(f"found {ecsvstr['Items']}")
        return {
            'statusCode': 200,
            'body': json.dumps(ecsvstr['Items'])
        }
    else:
        if 'dtstr' in qs:
            dtstr = qs['dtstr'] 
        else:
            dtstr = 'latest'
        maxitems = 200
        if dtstr == 'latest':
            maxitems = 100
        if 'enddtstr' in qs:
            dtstr2 = qs['enddtstr'] 
        else:
            dtstr2 = datetime.datetime.now().strftime('M%Y%m%d_%H')
        statid = None
        if 'statid' in qs:
            statid = qs['statid']
        fmt = None
        incxml = False
        trueimg = False
        if 'fmt' in qs:
            fmt = qs['fmt']
            if fmt == 'withxml':
                incxml = True
                fmt = 'json'
            elif fmt == 'trueimg': 
                trueimg = True
                fmt = 'json'
        conttoken = None
        if 'conttoken' in qs:
            conttoken = qs['conttoken']
        #print(dtstr, dtstr2, statid, maxitems)
        if trueimg:
            retval = getTrueImgs(dtstr, dtstr2, statid, ddb=ddb)
        else:
            retval = getImageUrls(dtstr, dtstr2, statid, conttoken, maxitems, includexml=incxml, ddb=ddb)
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
