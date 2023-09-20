#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
from boto3.dynamodb.conditions import Key
import json


def getLiveImages(dtstr):
    ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('live')
    resp = table.query(IndexName='month-image_name-index', 
                       KeyConditionExpression=Key('month').eq(dtstr[4:6]) & Key('image_name').begins_with(f'M{dtstr}'),
                       ProjectionExpression='image_name')
    return resp


def lambda_handler(event, context):
    #print(event)
    qs = event['queryStringParameters']
    patt = qs['pattern']
    print(f'searching for {patt}')
    ecsvstr = getLiveImages(patt)
    print(f"found {ecsvstr['Items']}")
    return {
        'statusCode': 200,
        'body': json.dumps(ecsvstr['Items'])
    }


if __name__ == '__main__':
    ecsvstr = getLiveImages('20230225_2101')
    print(ecsvstr)
