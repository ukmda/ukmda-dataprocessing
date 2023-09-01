#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
import os
import datetime 
import json


def _getCamLoc(camid):
    s3 = boto3.client('s3', region_name='eu-west-2')
    tmpdir = os.getenv('TMP', default='/tmp')
    localf = os.path.join(tmpdir, 'camera-details.csv')
    buck = os.getenv('ARCHBUCKET', default='ukmda-shared')
    s3.download_file(buck, 'consolidated/camera-details.csv', localf)
    camdets = open(localf, 'r').readlines()
    os.remove(localf)
    mtchs = [cam for cam in camdets if camid in cam]
    if len(mtchs) == 0:
        return None
    for li in mtchs:
        spls = li.split(',')
        active = int(spls[-1].strip())
        if active == 1:
            return spls[0] + '/' + spls[1]
    return None


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
    buck_name = os.getenv('ARCHBUCKET', default='ukmda-shared')
    s3 = boto3.client('s3', region_name='eu-west-2')
    spls = patt.split('_')
    if len(spls) < 3:
        return 'incorrect pattern: should be eg UK0001_20230814_021123'
    try: 
        _ = datetime.datetime.strptime(spls[1], '%Y%m%d')
    except:
        return f'invalid date: {spls[1]} should be YYYYMMDD'
    try:
        _ = datetime.datetime.strptime(spls[2], '%H%M%S')
    except:
        return f'invalid time: {spls[2]}, should be HHMMSS'
    
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

    # specimen FITS files where available (useful for calibration)
    dtstr = patt.split('_')[1]
    camloc = _getCamLoc(camid)
    fullpatt = f'archive/{camloc}/{dtstr[:4]}/{dtstr[:6]}/{dtstr}/FF_{camid}'
    x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
    if x['KeyCount'] > 0:
        for k in x['Contents']:
            key = k['Key']
            url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
            fname = key.split('/')[-1] 
            flist.append({'filename': fname, 'url': url})


    # config file, platepars_all and ftpdetect
    gotcfg = False
    fname = '.config'
    fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr}'
    x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
    if x['KeyCount'] > 0:
        for k in x['Contents']:
            key = k['Key']
            if '.config' in key:
                url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                fname = key.split('/')[-1]
                flist.append({'filename': fname, 'url': url})
                gotcfg = True
            if gotcfg and 'FTPdetectinfo' in key:
                url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                fname = key.split('/')[-1]
                flist.append({'filename': fname, 'url': url})
            if gotcfg and 'platepars_all' in key:
                url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                fname = key.split('/')[-1]
                flist.append({'filename': fname, 'url': url})

    if gotcfg is False:
        dt = datetime.datetime.strptime(dtstr, '%Y%m%d')
        dtstr = (dt +datetime.timedelta(days = -1)).strftime('%Y%m%d')
        fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr}'
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                if 'config' in key:
                    url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                    fname = key.split('/')[-1]
                    flist.append({'filename': fname, 'url': url})
                    gotcfg = True
                if gotcfg and 'FTPdetectinfo' in key:
                    url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                    fname = key.split('/')[-1]
                    flist.append({'filename': fname, 'url': url})
                if gotcfg and 'platepars_all' in key:
                    url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': buck_name,'Key': key}, ExpiresIn=300)
                    fname = key.split('/')[-1]
                    flist.append({'filename': fname, 'url': url})
    return flist


def lambda_handler(event, context):
    #print(event)
    qs = event['queryStringParameters']
    if qs is not None:
        if 'pattern' in qs:
            patt = qs['pattern']
            data = getFBfiles(patt)
            return {
                'statusCode': 200,
                'body': json.dumps(data), 
            }
        else:
            return {
                'statusCode': 200,
                'body': 'usage: getFireballFiles?pattern=UKcccccc_YYYYmmdd_HHMMSS'
            }
    else:
        return {
            'statusCode': 200,
            'body': 'usage: getFireballFiles?pattern=UKcccccc_YYYYmmdd_HHMMSS'
        }


if __name__ == '__main__':
    res = getFBfiles('UK0006_20230421_2122')
    for rw in res:
        url = rw['url']
        fname = rw['filename']
        print(fname)
