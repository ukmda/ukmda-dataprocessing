#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd


def addRow(newdata=None, stationid=None, site=None, user=None, email=None, ddb=None, tblname='camdetails'):
    # add a row to the CamTimings table
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    if not newdata:
        newdata = {'stationid': stationid, 'site': site, 'humanName':user, 'eMail': email}
    table = ddb.Table(tblname)
    response = table.put_item(Item=newdata)
    print(response)
    return 


def loadLocationDetails(table='camdetails', ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table(table)
    res = table.scan()
    # strictly, should check for LastEvaluatedKey here, in case there was more than 1MB of data,
    # however that equates to around 30,000 users which i hope we never have... 
    values = res.get('Items', [])
    camdets = pd.DataFrame(values)
    camdets.sort_values(by=['stationid'], inplace=True)
    camdets.dropna(inplace=True)
    return camdets


# find matching entries based on stationid 
def findSite(stationid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('camdetails')
    response = table.query(KeyConditionExpression=Key('stationid').eq(stationid))
    try:
        items = response['Items']
        if len(items) > 0:
            return items[0]['site']
        else:
            return ''
    except Exception:
        print('error fetching record')
    return


# remove a row from the table keyed on stationid adn datestamp in yyyymmdd_hhmmss format
def deleteRow(stationid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('camdetails')
    try:
        table.delete_item(Key={'stationid': stationid})
    except Exception:
        pass
    return 


def getCamUpdateDate(camid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    resp = table.query(KeyConditionExpression=Key('camid').eq(camid),
                       IndexName = 'camid-CaptureNight-index',
                       ScanIndexForward=False,
                       Limit=1,
                       Select='SPECIFIC_ATTRIBUTES',
                       ProjectionExpression='CaptureNight')
    if len(resp['Items']) > 0:
        return int(resp['Items'][0]['CaptureNight'])
    else:
        return 0
