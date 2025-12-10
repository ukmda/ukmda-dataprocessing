#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
import os

from stationMaint2 import addRow, loadLocationDetails


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


def dumpCamTable(outdir, statdets=None, ddb=None, exportmindets=False):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    if exportmindets:
        statdets = statdets[['stationid', 'eMail']]
    statdets.to_csv(os.path.join(outdir,'camtable.csv'), index=False)
