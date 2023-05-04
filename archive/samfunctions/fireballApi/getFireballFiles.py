#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
import os
import datetime 
import json


def getFBfiles(patt):
    """
    Retrieve fireball files from the ukmon website that match a pattern

    Arguments:
        patt:      [str] pattern to match

    Notes:
        The function looks for an FF and FR file, and returns a presigned URL for each file
        plus for the config and platepar files. These can be used to download the files without
        needing special permission to AWS. The presigned URLs expire after 300 seconds. 
    """
    flist = []
    buck_name = os.getenv('ARCHBUCKET', default='ukmon-shared')
    s3 = boto3.client('s3', region_name='eu-west-2')
    fullpatt = f'fireballs/interesting/FF_{patt}'
    print(f'looking for {fullpatt} in {buck_name}')
    x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
    if x['KeyCount'] > 0:
        for k in x['Contents']:
            key = k['Key']
            url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
            fname = key.split('/')[-1]
            flist.append({'filename': fname, 'url': url})
    fullpatt = f'fireballs/interesting/FR_{patt}'
    x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
    if x['KeyCount'] > 0:
        for k in x['Contents']:
            key = k['Key']
            url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
            fname = key.split('/')[-1]
            flist.append({'filename': fname, 'url': url})
    # platepar file
    if len(flist) > 0: 
        camid = patt.split('_')[0]
        print(f'looking for config and platepar for {camid}')
        fullpatt = f'consolidated/platepars/{camid}'
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                #fname = key.split('/')[-1] # hardcoding it here
                flist.append({'filename': 'platepar_cmn2010.cal', 'url': url})
        # config file
        dtstr = patt.split('_')[1]
        gotcfg = False
        fname = '.config'
        fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr}'
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                if fname in key:
                    url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                    fname = key.split('/')[-1]
                    flist.append({'filename': fname, 'url': url})
                    gotcfg = True
        if gotcfg is False:
            dt = datetime.datetime.strptime(dtstr, '%Y%m%d')
            dtstr = (dt +datetime.timedelta(days = -1)).strftime('%Y%m%d')
            fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr}'
            x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
            if x['KeyCount'] > 0:
                for k in x['Contents']:
                    key = k['Key']
                    if fname in key:
                        url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                        fname = key.split('/')[-1]
                        flist.append({'filename': fname, 'url': url})
                        gotcfg = True
    return flist


def lambda_handler(event, context):
    #print(event)
    qs = event['queryStringParameters']
    patt = qs['pattern']
    data = getFBfiles(patt)
    return {
        'statusCode': 200,
        'body': json.dumps(data), 
    }


if __name__ == '__main__':
    res = getFBfiles('UK0006_20230421_2122')
    for rw in res:
        url = rw['url']
        fname = rw['filename']
        print(fname)
