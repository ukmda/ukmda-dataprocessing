#
# Create and access dynamodb tables containing camera upload timings etc
#

import boto3
import os
import glob
from boto3.dynamodb.conditions import Key

def createCamTimingsTable(ddb=None):
    
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")

    # Create the DynamoDB table.
    tbl='ukmon_uploadtimes'
    try:
        table = ddb.create_table(
            TableName=tbl,
            KeySchema=[
                {
                    'AttributeName': 'stationid',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'dtstamp',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'stationid', 'AttributeType': 'S'
                },
                {
                    'AttributeName': 'dtstamp', 'AttributeType': 'S'
                },
                {
                    'AttributeName': 'uploaddate', 'AttributeType': 'N'
                }
            ],
            #ProvisionedThroughput={
            #    'ReadCapacityUnits': 0,
            #    'WriteCapacityUnits': 0
            #},
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes= [
                {
                    "IndexName": "uploaddate-stationid-index",
                    "KeySchema": [
                        {
                            "AttributeName": "uploaddate",
                            "KeyType": "HASH"
                        },
                        {
                            "AttributeName": "stationid",
                            "KeyType": "RANGE"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "IndexStatus": "ACTIVE",
                    #"ProvisionedThroughput": {
                    #    "NumberOfDecreasesToday": 0,
                    #    "ReadCapacityUnits": 0,            
                    #    "WriteCapacityUnits": 0
                    #},
                }
            ]
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=tbl)
    except:
        print(f'table {tbl} already exists')
        table = ddb.Table(tbl)

    # Wait until the table exists.
    print(table.creation_date_time)
    return 


# Print out some data about the table - works for any table
def testable(tbl, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table(tbl)
    print(table.creation_date_time)
    print(table.item_count)
    return


# delete a table - works for any table
def deleteTable(tbl, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table(tbl)
    table.delete()
    return 


# add a row to the CamTimings table
def addRowCamTimings(s3bucket, s3object, ftpname, ddb=None):
    s3c = boto3.client('s3')
    dtstamp = s3c.head_object(Bucket=s3bucket, Key=s3object)['LastModified']

    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")

    table = ddb.Table('ukmon_uploadtimes')
    spls = ftpname.split('_')
    print(spls[0], dtstamp)
    if spls[-1] == 'manual.txt':
        manflag = '_man'
        manual = True
    else:
        manflag = ''
        manual = False
    uploaddate = dtstamp.strftime('%Y%m%d')
    uploadtime = dtstamp.strftime('%H%M%S')
    table.put_item(
        Item={
            'stationid': spls[1],
            'dtstamp': uploaddate + '_' + uploadtime + manflag,
            'uploaddate': int(uploaddate),
            'uploadtime': int(uploadtime),
            'manual': manual
        }
    )    
    return 


# find matching entries based on stationid and upload date in yyyymmdd format
def findRowCamTimings(stationid, uploaddate, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('ukmon_uploadtimes')
    response = table.query(
        KeyConditionExpression=Key('stationid').eq(stationid) & Key('dtstamp').begins_with(uploaddate)
    )
    try:
        items = response['Items']
        for item in items:
            print(item['stationid'], item['uploaddate'], item['uploadtime'],item['manual'])
    except Exception:
        print('record not found')
    return


# find matching entries based on stationid and upload date in yyyymmdd format
def getDayCamTimings(uploaddate, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('ukmon_uploadtimes')
    response = table.query(KeyConditionExpression=Key(Key('dtstamp').begins_with(uploaddate)))

    try:
        items = response['Items']
        for item in items:
            print(item['stationid'], item['uploaddate'], item['uploadtime'],item['manual'])
    except Exception:
        print('record not found')
    return


# read a row based on stationid and datestamp
def readRowCamTimings(stationid, dtstamp, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('ukmon_uploadtimes')
    response = table.get_item(Key={ 'stationid': stationid,'dtstamp': dtstamp })
    try:
        item = response['Item']
        print(item['stationid'], item['uploaddate'], item['uploadtime'],item['manual'])
    except Exception:
        print('record not found')
    return


# remove a row from the table keyed on stationid adn datestamp in yyyymmdd_hhmmss format
def deleteRowCamTimings(stationid, dtstamp, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('ukmon_uploadtimes')
    table.delete_item(Key={'stationid': stationid, 'dtstamp': dtstamp})
    return 


def backPopulate(stationid):
    s3bucket='ukmon-shared'

    fldrs = glob.glob1(f'/home/ec2-user/ukmon-shared/matches/RMSCorrelate/{stationid}/', '*')
    for fldr in fldrs:
        s3objects = glob.glob1(f'/home/ec2-user/ukmon-shared/matches/RMSCorrelate/{stationid}/{fldr}/', 'FTPd*')
        if len(s3objects) > 0:
            s3obj = s3objects[0]
            fullobj = f'matches/RMSCorrelate/{stationid}/{fldr}/{s3obj}'
            print(fullobj, s3obj)
            addRowCamTimings(s3bucket, fullobj, s3obj)


if __name__ == '__main__':
    stationids = glob.glob1(f'/home/ec2-user/ukmon-shared/matches/RMSCorrelate/', 'UK*')
    for statid in stationids:
        backPopulate(statid)
