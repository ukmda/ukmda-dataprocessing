# Copyright (C) 2018-2023 Mark McIntyre

import os
import boto3
import botocore
import datetime 


def testAndCopyFile(s3cli, srcfldr):
    s3bucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]

    locspls = srcfldr.split('/')
    camid = locspls[2]

    plap = srcfldr +'/platepars_all_recalibrated.json'
    try:
        s3cli.head_object(Bucket=s3bucket, Key=plap)
    except botocore.exceptions.ClientError as e:    
        if e.response['Error']['Code'] == '404':
            print(f'platepars file not available in {srcfldr}')
            return False
        else:
            print(f'some other error reading {srcfldr}')
            return False
    else:
        print(f'platepars file exists in {srcfldr}')

        objlist = s3cli.list_objects_v2(Bucket=s3bucket, Prefix=srcfldr +'/FTPdetect')
        if objlist['KeyCount'] > 0:
            keys = objlist['Contents']
            fname = keys[0]['Key']
            _, fname = os.path.split(fname)
            fname = fname[14:]
            outdir, _ = os.path.splitext(fname)
            outf = 'matches/RMSCorrelate/' + camid + '/' + outdir + '/platepars_all_recalibrated.json'
            print(outf)
            src = {'Bucket': s3bucket, 'Key': plap}
            s3cli.copy_object(Bucket=s3bucket, Key=outf, CopySource=src)
            return True
        else:
            return False


def gatherMissedPlatepars(dtstr):

    sts_client = boto3.client('sts')
    assumed_role_object=sts_client.assume_role(
        RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
        RoleSessionName="AssumeRoleSession1")
    
    # Use the temporary credentials that AssumeRole returns to connections
    credentials=assumed_role_object['Credentials']        

    logcli = boto3.client('logs', 
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'], 
        region_name='eu-west-2')

    s3cli = boto3.client('s3', 
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'], 
        region_name='eu-west-2')

    chkdt = datetime.datetime.strptime(dtstr, '%Y%m%d')
    print(chkdt)
    uxt = int(chkdt.timestamp()*1000)

    badcams=[]
    response = logcli.filter_log_events(
        logGroupName="/aws/lambda/consolidateFTPdetect",
        startTime=uxt,
        filterPattern="platepars_all is missing",
        limit=1000)
    if len(response['events']) > 0:
        for i in range(len(response['events'])):
            msg = response['events'][i]['message'].strip()
            spls = msg.split(' ')
            fldrtotest = spls[-1]
            res = testAndCopyFile(s3cli, fldrtotest)
            badcams.append([fldrtotest, res])
    while True:
        currentToken = response['nextToken']
        response = logcli.filter_log_events(
            logGroupName="/aws/lambda/consolidateFTPdetect",
            startTime=uxt,
            filterPattern="platepars_all is missing",
            nextToken = currentToken,
            limit=1000)
        if len(response['events']) > 0:
            for i in range(len(response['events'])):
                msg = response['events'][i]['message'].strip()
                spls = msg.split(' ')
                fldrtotest = spls[-1]
                res = testAndCopyFile(s3cli, fldrtotest)
                badcams.append([fldrtotest, res])
        if 'nextToken' not in response:
            break
    
    print(badcams)
    return 


if __name__ == '__main__':
    dtstr = '20220529'
    gatherMissedPlatepars(dtstr)
