# copyright 2023- Mark McIntyre
# all rights reserved

"""
 a function to compress the ukmda-shared/archive data from before the current year

usage:
    1) python compressOldArchiveData.py - this will scan and compress ALL data from prior years
    2) python compressOldArchiveData.py "archive/somefolder" will scan and compress only the named location folder

note that any MP4 or AVI files that have been uploaded to this area are removed by this process. The videos should be 
on the website in ukmda-website/img/mp4s in mp4 format
"""

import boto3
import zipfile
import io
import sys
import datetime 

maxyear = datetime.datetime.now().year - 1

s3 = boto3.client('s3')
s3res = boto3.resource('s3')


def listLocations(srcbucket='ukmda-shared', prefixstr='archive/'):
    """
    list all top level folders in a particular prefix
    parameters:
        srcbucket: [string] bucket name, default ukmda-shared
        prefixstr: [string] prefix, default archive/ - note must have terminal slash

    returns:
        list of prefixes
    """
    response = s3.list_objects_v2(Bucket=srcbucket, Prefix=prefixstr, Delimiter='/')
    if 'CommonPrefixes' in response:
        return response['CommonPrefixes']
    else:
        return []
    

def listCameras(srcbucket='ukmda-shared', location='archive/Tackley/'):
    response = s3.list_objects_v2(Bucket=srcbucket, Prefix=location, Delimiter='/')
    if 'CommonPrefixes' in response:
        return response['CommonPrefixes']
    else:
        return []


def listYears(srcbucket='ukmda-shared', camid='archive/Tackley/c1/'):
    response = s3.list_objects_v2(Bucket=srcbucket, Prefix=camid, Delimiter='/')
    if 'CommonPrefixes' in response:
        return response['CommonPrefixes']
    else:
        return []
    

def getAllS3Objects(s3, **base_kwargs):
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield from response.get('Contents', [])
        if not response.get('IsTruncated'):  # At the end of the list?
            break
        continuation_token = response.get('NextContinuationToken')


def deleteFiles(flist, srcbucket='ukmda-shared'):
    chunk_size = 900
    chunked_list = [flist[i:i + chunk_size] for i in range(0, len(flist), chunk_size)]
    for ch in chunked_list:
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': k} for k in ch]
        s3.delete_objects(Bucket=srcbucket, Delete=delete_keys)
    return 


def compressObjects(srcbucket='ukmda-shared', camprefix=None):
    lcmprefixes = []
    if camprefix is None:
        locations = listLocations()
        for location in locations:
            camids = listCameras(location=location['Prefix'])
            for camid in camids:
                years = listYears(camid=camid['Prefix'])
                for year in years:
                    lcmprefix = year['Prefix'][:-1]
                    lcmprefixes.append(lcmprefix)
    else:
        spls = camprefix[:-1].split('/')
        print(spls)
        if len(spls) < 3:
            camids = listCameras(location=camprefix)
            for camid in camids:
                years = listYears(camid=camid['Prefix'])
                for year in years:
                    lcmprefix = year['Prefix'][:-1]
                    lcmprefixes.append(lcmprefix)
        else:
            years = listYears(camid=camprefix)
            for year in years:
                lcmprefix = year['Prefix'][:-1]
                lcmprefixes.append(lcmprefix)

    for lcmprefix in lcmprefixes:
        spls = lcmprefix.split('/')
        zfname = f'{spls[0]}/{spls[1]}/{spls[1]}_{spls[2]}_{spls[3]}.zip'
        try: 
            if int(spls[3]) > maxyear or 'miscellan' in spls[3] or 'profiles' in spls[3]: 
                continue
        except Exception:
            pass
        if 'testpi' in lcmprefix:
            continue
        bucket = s3res.Bucket(srcbucket)
        files = [os.key for os in bucket.objects.filter(Prefix=lcmprefix)]
        mp4files = [file for file in files if '.mp4' in file]
        deleteFiles(mp4files)
        avifiles = [file for file in files if '.avi' in file]
        deleteFiles(avifiles)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for key in files:
                if '.mp4' not in key and '.avi' not in key:
                    print(key)
                    data = s3.get_object(Bucket=srcbucket, Key=key)
                    content = data['Body'].read()
                    zipf.writestr(key, content)
                
        # Upload the zip file to the target bucket
        zip_buffer.seek(0)
        print(f'uploading {zfname}')
        s3.upload_fileobj(zip_buffer, srcbucket, zfname)
        # now delete the files
        print(f'deleting files from {lcmprefix}')
        deleteFiles(files)
            

if __name__ == '__main__':
    source_bucket = 'ukmda-shared'
    prefix_str = None
    if len(sys.argv) > 1:
        prefix_str = sys.argv[1]
        if prefix_str[-1] != '/':
            prefix_str = prefix_str + '/'
    print(f'compressing {prefix_str}')
    compressObjects(source_bucket, prefix_str)
