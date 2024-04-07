#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd
import os


def addRow(newdata=None, stationid=None, site=None, user=None, email=None, ddb=None, 
           direction=None, camtype=None, active=None, createdate=None, tblname='camdetails'):
    # add a row to the CamTimings table
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    if not newdata:
        newdata = {'stationid': stationid, 'site': site, 'humanName':user, 'eMail': email, 
                   'direction': direction, 'camtype': camtype, 'active': active, 'created': createdate,
                   'oldcode': stationid}
    table = ddb.Table(tblname)
#    resp = table.get_item(Key={'stationid': stationid, 'site': site})
#    if 'Item' in resp:
#        if 'created' in resp['Item']:
#            newdata['created'] = resp['Item']['created']
    response = table.put_item(Item=newdata)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(response)
    return 


def addCreatedDate():
    bucket = 'ukmda-shared'
    s3 = boto3.client('s3')
    camdets = loadLocationDetails()
    for _, cam in camdets.iterrows():
        res = s3.list_objects_v2(Bucket=bucket,Prefix=f'matches/RMSCorrelate/{cam["stationid"]}/', Delimiter='/')
        if 'CommonPrefixes' in res:
            earliest_fldr = os.path.split(res['CommonPrefixes'][0]['Prefix'][:-1])[1]
            created = earliest_fldr.split('_')[1]
        else:
            created = ''
        newdata = {'stationid': cam['stationid'], 'site': cam['site'], 'humanName':cam['humanName'], 'eMail': cam['eMail'], 
                    'direction': cam['direction'], 'camtype': cam['camtype'], 'active': cam['active'], 
                    'created': created, 'oldcode': cam['stationid']}
        print(newdata)
        addRow(newdata)
    return 


def loadLocationDetails(table='camdetails', ddb=None, loadall=False):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table(table)
    res = table.scan()
    # strictly, should check for LastEvaluatedKey here, in case there was more than 1MB of data,
    # however that equates to around 30,000 users which i hope we never have... 
    values = res.get('Items', [])
    camdets = pd.DataFrame(values)
    camdets.sort_values(by=['stationid'], inplace=True)
    if not loadall:
        camdets.dropna(inplace=True, subset=['eMail','humanName','site'])
    camdets['camtype'] = camdets['camtype'].astype(int)
    camdets['active'] = camdets['active'].astype(int)
    return camdets


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


def findLocationInfo(srchstring, ddb=None, statdets=None):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    s1 = statdets[statdets.stationid.str.contains(srchstring)]
    s2 = statdets[statdets.eMail.str.contains(srchstring)]
    s3 = statdets[statdets.humanName.str.contains(srchstring)]
    s4 = statdets[statdets.site.str.contains(srchstring)]
    srchres = pd.concat([s1, s2, s3, s4])
    srchres.drop(columns=['oldcode','active','camtype'], inplace=True)
    return srchres


def cameraExists(stationid=None, location=None, direction=None, ddb=None, statdets=None):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    if stationid:
        if len(statdets[statdets.stationid == stationid]) > 0:
            return True
    if location and direction:
        s1 = statdets[statdets.site == location]
        if len(s1) > 0:
            if len(s1[s1.direction == direction]) > 0:
                return True
    return False


def dumpCamTable(outdir, statdets=None, ddb=None, exportmindets=False):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    if exportmindets:
        statdets = statdets[['stationid', 'eMail']]
    statdets.to_csv(os.path.join(outdir,'camtable.csv'), index=False)


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
