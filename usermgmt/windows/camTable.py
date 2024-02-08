#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd


def addRow(newdata=None, stationid=None, site=None, user=None, email=None, ddb=None, 
           direction=None, camtype=None, active=None, tblname='camdetails'):
    # add a row to the CamTimings table
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    if not newdata:
        newdata = {'stationid': stationid, 'site': site, 'humanName':user, 'eMail': email, 
                   'direction': direction, 'camtype': camtype, 'active': active}
    table = ddb.Table(tblname)
    response = table.put_item(Item=newdata)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(response)
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

   
def mergeTables():
    # one off to merge in the CSV file
    conn = boto3.Session(profile_name='ukmda_maint')
    s3 = conn.client('s3')
    ddb = conn.resource('dynamodb', region_name='eu-west-2')
    locationdets = loadLocationDetails(ddb=ddb, loadall=True)
    camfile = 'consolidated/camera-details.csv'
    localfile = 'c:/temp/camera-details.csv'
    s3.download_file(Bucket='ukmda-shared', Key=camfile, Filename=localfile)
    caminfo = pd.read_csv(localfile)
    locationdets = locationdets[locationdets.direction.isna()]
    for _,rw in locationdets.iterrows():
        #print('ddb:', rw.stationid, rw.site, rw.eMail, rw.humanName, rw.direction, rw.camtype, rw.active, rw.oldcode)
        thiscam = caminfo[caminfo.dummycode==rw.stationid]
        if len(thiscam) > 1:
            thiscam = thiscam[caminfo.active==1]
        if len(thiscam) == 1:
            csvdata = thiscam.iloc[0]
            em = str(rw.eMail)
            if em == 'nan':
                em = 'unknown@unknown'
            hn = str(rw.humanName)
            if hn == 'nan':
                hn = 'unknown'
            direc = str(csvdata.sid)
            if direc == 'nan':
                direc = ''
            newdata = {'stationid': rw.stationid, 'site': rw.site, 'humanName':hn, 'eMail': em, 
                    'direction': direc, 'camtype': str(csvdata.camtype), 'active': str(csvdata.active), 'oldcode': csvdata.dummycode}
            print(newdata)
            addRow(newdata, ddb=ddb)
        else:
            print(f'csv: {len(thiscam)} matches for {rw.stationid}')
