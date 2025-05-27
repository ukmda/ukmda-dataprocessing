# Copyright (C) 2018-2023 Mark McIntyre
import json
from boto3.dynamodb.conditions import Key
import boto3


def lambda_handler(event, context):
    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    camid = qs['camid']

    ddb = boto3.resource('dynamodb', region_name='eu-west-2') 
    table = ddb.Table('camdetails')
    res = table.query(KeyConditionExpression=Key('stationid').eq(camid))
    if res['Count'] > 0:
        # convert Decimals to str
        for i in range(0, res['Count']):
            print(res['Items'][i])
            res['Items'][i]['active']=str(res['Items'][i]['active'])
            res['Items'][i]['camtype']=str(res['Items'][i]['camtype'])        
        return {
            'statusCode': 200,
            'body': json.dumps(res['Items'])
        }
    else:
        return {'statusCode': 200, 'body': '{}'}
