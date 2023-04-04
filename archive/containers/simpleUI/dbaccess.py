# Copyright (C) 2018-2023 Mark McIntyre

import boto3
import pandas as pd 

def getS3Client():
    sts_client = boto3.client('sts')
    try: 
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            RoleSessionName="AssumeRoleSession1")

        credentials=assumed_role_object['Credentials']

        s3 = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])    
    except:
        with open('awskeys','r') as inf:
            lis = inf.readlines()
        s3 = boto3.resource('s3',
            aws_access_key_id=lis[0].strip(),
            aws_secret_access_key=lis[1].strip(),
            region_name = 'eu-west-2')
    return s3


def getCamList():
    s3 = getS3Client()
    srcbucket = 'ukmon-shared'
    srckey = 'consolidated/camera-details.csv'
    targfile = '/tmp/camera-details.csv'
    s3.meta.client.download_file(srcbucket, srckey, targfile)
    df = pd.read_csv(targfile)
    return df


def pushCamList():
    s3 = getS3Client()
    srcbucket = 'ukmon-shared'
    srckey = 'consolidated/camera-details.csv'
    targfile = '/tmp/camera-details.csv'
    s3.meta.client.upload_file(targfile, srcbucket, srckey)
    return

    
