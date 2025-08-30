# copyright 2023- Mark McIntyre
# all rights reserved

"""
 a set of functions to 
    - compress the ukmda-shared/archive data from before the current year
    - remove unused but easily recreated files from the website
    - remove links to the old downloadable zip file

usage:
    1) python compressOldArchiveData.py - will scan and compress ALL data from prior years
    2) python compressOldArchiveData.py "archive/somefolder" - will scan and compress only the named location folder
    3) python compressOldArchiveData.py prune_website - will scan and remove unused files from the website 
    3) python compressOldArchiveData.py prune_website reports/2024/202401 - will scan and remove unused files 
        from the named location and below

note that any MP4 or AVI files that have been uploaded to this area are removed by this process. The videos should be 
on the website in ukmda-website/img/mp4s in mp4 format
"""

import boto3
import zipfile
import io
import os
import datetime 
import argparse

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
    

"""
Not used
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
"""

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


def moveJpgsAndMp4s(source_bucket, yr, ym):
    print(f'moving jpgs and mp4s from {ym}')
    bucket = s3res.Bucket(source_bucket)
    files = [os.key for os in bucket.objects.filter(Prefix=f'reports/{yr}/orbits/{ym}/')]
    jpgs = [x for x in files if '.jpg' in x or '.mp4' in x]
    print(f'moving {len(jpgs)} jpgs or mp4s')
    for jpg in jpgs:
        print(jpg)
        keyname = os.path.split(jpg)[1]
        if '.jpg' in keyname:
            newkey = f'img/single/{yr}/{ym}/{keyname}'
        else:
            newkey = f'img/mp4/{yr}/{ym}/{keyname}'
        s3.copy_object(Bucket=source_bucket, 
                       CopySource={'Bucket':source_bucket,'Key':jpg}, 
                       Key=newkey, MetadataDirective='COPY')
        s3.delete_object(Bucket=source_bucket, Key=jpg)
    jpgfldrs = [os.path.split(x)[0] for x in jpgs]
    jpgfldrs = list(set(jpgfldrs))
    jpgfldrs.sort()
    print(f'updating {len(jpgfldrs)} indexes')
    for fldr in jpgfldrs:
        print(fldr)
        idx = f'{fldr}/index.html'
        rootdir = os.path.split(idx)[0]
        try:
            s3.download_file(source_bucket, idx, f'/tmp/oldindex.html')
        except Exception:
            continue
        lis = open('/tmp/oldindex.html', 'r').readlines()
        # skip files that dont have the line in them
        mtch = [li for li in lis if '.jpg' in li or '.mp4' in li]
        if len(mtch) == 0: 
            continue
        with open('/tmp/newindex.html', 'w') as outf:
            for li in lis:
                if '.jpg' in li and '/img/single/' not in li:
                    newpth=f'/img/single/{yr}/{ym}/'
                    li = li.replace('a href="', f'a href="{newpth}')
                    li = li.replace('img src="', f'img src="{newpth}')
                if '.mp4' in li and '/img/mp4/' not in li:
                    newpth=f'/img/mp4/{yr}/{ym}/'
                    li = li.replace('a href="', f'a href="{newpth}')
                    li = li.replace('source src="', f'source src="{newpth}')
                    li = li.replace(rootdir, '')
                li = li.replace('//', '/')
                li = li.replace('//', '/')
                outf.write(li)
        extraargs = {'ContentType': 'text/html'}
        s3.upload_file('/tmp/newindex.html', source_bucket, idx, ExtraArgs=extraargs)
    print('done')

def fixBrokenIndexes(source_bucket, yr, ym):
    bucket = s3res.Bucket(source_bucket)
    files = [os.key for os in bucket.objects.filter(Prefix=f'reports/{yr}/orbits/{ym}/')]
    idxs = [x for x in files if 'index.html' in x]
    for idx in idxs:
        print(idx)
        s3.download_file(source_bucket, idx, f'/tmp/oldindex.html')
        lis = open('/tmp/oldindex.html', 'r').readlines()
        rootdir = os.path.split(idx)[0]
        # skip files that dont have the line in them
        mtch = [li for li in lis if '.jpg' in li or '.mp4' in li]
        if len(mtch) == 0: 
            continue
        with open('/tmp/newindex.html', 'w') as outf:
            for li in lis:
                if '.jpg' in li and '/img/single/' not in li:
                    newpth=f'/img/single/{yr}/{ym}/'
                    li = li.replace('a href="', f'a href="{newpth}')
                    li = li.replace('img src="', f'img src="{newpth}')
                if '.mp4' in li and '/img/mp4/' not in li:
                    newpth=f'/img/mp4/{yr}/{ym}/'
                    li = li.replace('a href="', f'a href="{newpth}')
                    li = li.replace('source src="', f'source src="{newpth}')
                    li = li.replace(rootdir, '')
                li = li.replace('//', '/')
                li = li.replace('//', '/')
                outf.write(li)
#            for li in lis:
#                if '.jpg' in li:
#                    oldpth = f'/img/single/{yr}/{ym}'
#                    newpth = f'/img/single/{yr}/{ym}/'
#                    li = li.replace(f'a href="{oldpth}', f'a href="{newpth}')
#                    li = li.replace(f'img src="{oldpth}', f'img src="{newpth}')
#                if '.mp4' in li:
#                    oldpth = f'/img/single/{yr}/{ym}'
#                    newpth=f'/img/mp4/{yr}/{ym}/'
#                    li = li.replace(f'a href="{oldpth}', f'a href="{newpth}')
#                    li = li.replace(f'source src="{oldpth}', f'source src="{newpth}')
#                    li = li.replace(rootdir, '')
#                li = li.replace('//', '/')
#                li = li.replace('//', '/')
#                outf.write(li)
        extraargs = {'ContentType': 'text/html'}
        s3.upload_file('/tmp/newindex.html', source_bucket, idx, ExtraArgs=extraargs)


def updateIndexes(idxs, source_bucket):
    for idx in idxs:
        if len(idx.split('/')) < 7:
            continue
        s3.download_file(source_bucket, idx, f'/tmp/oldindex.html')
        lis = open('/tmp/oldindex.html', 'r').readlines()
        # skip files that dont have the line in them
        mtch = [li for li in lis if 'download a zip of the' in li]
        if len(mtch) == 0: 
            continue
        with open('/tmp/newindex.html', 'w') as outf:
            for li in lis:
                if 'download a zip of the' in li:
                    continue
                outf.write(li)
        extraargs = {'ContentType': 'text/html'}
        s3.upload_file('/tmp/newindex.html', source_bucket, idx, ExtraArgs=extraargs)
    return 


def pruneObjects(source_bucket, prefix_str, force_reindex=False):
    spls = prefix_str.split('/')
    bucket = s3res.Bucket(source_bucket)
    if len(spls) < 3:
        years = listYears(source_bucket, prefix_str)
        years = [x['Prefix'] for x in years if 'reports/20' in x['Prefix']]
    else:
        years = [f'reports/{spls[1]}/']
    for yr in years:
        print(f'processing {yr}')
        yr_prefix = f'{yr}orbits/'
        if len(spls) > 3:
            mths = [f'{yr_prefix}{spls[2]}/']
        else:
            mths = listYears(source_bucket, yr_prefix)
            mths = [x['Prefix'] for x in mths if 'csv/' not in x['Prefix'] and 'plots/' not in x['Prefix']]
        for mth in mths:
            print(f'processing {mth}')
            files = [os.key for os in bucket.objects.filter(Prefix=mth)]
            print('purging zip files')
            zipfs = [file for file in files if '.zip' in file]
            deleteFiles(zipfs, source_bucket)
            if len(zipfs) > 0 or force_reindex:
                print('updating indexes')
                idxs = [file for file in files if '/index.html' in file]
                updateIndexes(idxs, source_bucket)
            print('purging pngs')
            spatres = [file for file in files if '_spatial_residuals.png' in file and '_all' not in file]
            deleteFiles(spatres, source_bucket)
            print('purging kml and ftpdetect')
            others = [file for file in files if '.kml' in file or 'FTPdetectinfo' in file]
            deleteFiles(others, source_bucket)
            print('purging csv')
            csvs = [file for file in files if '.csv' in file]
            deleteFiles(csvs, source_bucket)
    return 
            

if __name__ == '__main__':
    prefix_str = None

    arg_parser = argparse.ArgumentParser(description='Compress, prune or clear down older data')

    arg_parser.add_argument('command_str', nargs=1, metavar='COMMAND_STR', type=str,
        help='action to take. Options are COMPRESS or PRUNE to compress archive files or prune the website.')

    arg_parser.add_argument('-f', '--folder', help="""area to act on, eg "Tackley" or "2025/202504".""")
    
    arg_parser.add_argument('-i', '--reindex', action='store_true', help="""force recreation of indexes".""")

    args = arg_parser.parse_args()

    if args.command_str[0].upper() == 'COMPRESS':
        source_bucket = 'ukmda-shared'
        if args.folder:
            prefix_str = 'archive/' + prefix_str
            prefix_str = args.folder
            if prefix_str[-1] != '/':
                prefix_str = prefix_str + '/'
        print(f'compressing {prefix_str}')
        compressObjects(source_bucket, prefix_str)

    if args.command_str[0].upper() == 'PRUNE':
        source_bucket = 'ukmda-website'
        if args.folder:
            prefix_str = 'reports/' + args.folder
            if prefix_str[-1] != '/':
                prefix_str = prefix_str + '/'
        force_reindex = False
        if args.reindex:
            force_reindex = True
        print(f'pruning {prefix_str} and forcing reindex')
        pruneObjects(source_bucket, prefix_str, force_reindex)
