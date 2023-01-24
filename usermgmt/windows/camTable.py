#
# Create and access dynamodb tables containing camera upload timings etc
#

import boto3
from boto3.dynamodb.conditions import Key


def createTable(ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')

    # Create the DynamoDB table.
    tbl='ukmon_camdetails'
    try:
        table = ddb.create_table(
            TableName=tbl,
            KeySchema=[
                {
                    'AttributeName': 'stationid',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'site',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'stationid', 'AttributeType': 'S'
                },
                {
                    'AttributeName': 'site', 'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=tbl)
    except:
        print(f'table {tbl} already exists')
        table = ddb.Table(tbl)

    # Wait until the table exists.
    print(table.creation_date_time)
    return 


# Print out some data about the table - works for any table
def testTable(tbl, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1') 
    table = ddb.Table(tbl)
    print(table.creation_date_time)
    print(table.item_count)
    return


# delete a table - works for any table
def deleteTable(tbl, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table(tbl)
    table.delete()
    return 


# add a row to the CamTimings table
def addRow(stationid, siteid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = ddb.Table('ukmon_camdetails')
    response = table.put_item(
        Item={
            'stationid': stationid,
            'site': siteid
        }   
    )    
    print(response)
    return 


# find matching entries based on stationid 
def findSite(stationid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table('ukmon_camdetails')
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
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = ddb.Table('ukmon_camdetails')
    table.delete_item(Key={'stationid': stationid})
    return 


def backPopulate():
    ddb = boto3.resource('dynamodb', region_name='eu-west-1') 
    with open('f:/videos/meteorcam/ukmondata/consolidated/camera-details.csv') as inf:
        lis = inf.readlines()
    for li in lis:
        spls = li.split(',')
        loc = spls[0]
        stationid = spls[5]
        addRow(stationid, loc, ddb)
