# Copyright Mark McIntyre, 2024-

# batch delete rows from the updatetimes table 

import boto3
import datetime
from boto3.dynamodb.conditions import Key
import os


def deleteRows():
    archprof = os.getenv('ADM_PROFILE', default='ukmda_admin')
    conn = boto3.Session(profile_name=archprof)
    ddb = conn.resource('dynamodb', region_name='eu-west-2')
    tbl = 'uploadtimes'
    idx = 'uploaddate-stationid-index'
    table = ddb.Table(tbl)
    currdt = datetime.datetime.now()
    for i in range(90,200):
        seldt = currdt + datetime.timedelta(days=-i)
        seldtstr = seldt.strftime('%Y%m%d')
        response = table.query(IndexName=idx, KeyConditionExpression=Key('uploaddate').eq(int(seldtstr)))
        items_to_delete = response['Items']
        with table.batch_writer() as batch:
            for item in items_to_delete:
                print(f'deleting {item["stationid"]} on {item["dtstamp"]}')
                response = batch.delete_item(Key={'dtstamp': item['dtstamp'], 'stationid': item['stationid']})


def updateMissingExpiryDate():
    archprof = os.getenv('ADM_PROFILE', default='ukmda_admin')
    conn = boto3.Session(profile_name=archprof)
    ddb = conn.resource('dynamodb', region_name='eu-west-2')
    tbl = 'uploadtimes'
    idx = 'uploaddate-stationid-index'
    table = ddb.Table(tbl)
    currdt = datetime.datetime.now()
    for i in range(0,92):
        seldt = currdt + datetime.timedelta(days=-i)
        seldtstr = seldt.strftime('%Y%m%d')
        response = table.query(IndexName=idx, KeyConditionExpression=Key('uploaddate').eq(int(seldtstr)))
        items_to_update = response['Items']
        with table.batch_writer() as batch:
            for item in items_to_update:
                if 'ExpiryDate' not in item:
                    rundt = datetime.datetime.strptime(item['rundate'], '%Y%m%d_%H%M%S')
                    expdt = int((rundt + datetime.timedelta(days=90)).timestamp())
                    item['ExpiryDate'] = expdt
                    print(f'updating {item["stationid"]} on {item["dtstamp"]}')
                    response = batch.put_item(Item=item)
