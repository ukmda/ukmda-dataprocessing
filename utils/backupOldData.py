# copyright 2023- Mark McIntyre
# all rights reserved

# one-off script to create a backup of the legacy, UFO, data from s3://ukmda-shared/archive
#
# usage : python3 backupOldData.py /path/to/local {subfldr}
#
# where 
# /path/to/local is the target location to create the backup at
# subfldr is an optional subfolder to backup, for example "birmingham" would only backup that subfolder

import boto3
import sys
import os


def findFilesToBackup(archbucket, location, target):
    s3r = boto3.resource('s3')
    bucket = s3r.Bucket(archbucket)
    print(f'Backing up data from {archbucket}/{location}... ', end='')
    sys.stdout.flush()
    files = [os.key for os in bucket.objects.filter(Prefix=location)]
    fltfiles = [file for file in files if 'FTPdetect' in file or 'platepars_all' in file or '.config' in file or 'A.XML' in file]
    refltfiles = [file for file in fltfiles if '/2018' in file or '/2019' in file or '/2017' in file or '/2016' in file 
        or '/2015' in file or '/2014' in file or '/2013' in file or '/2012' in file]
    numimgs = len(refltfiles)
    backupFiles(refltfiles, archbucket, os.path.join(target, archbucket))
    print(f'Backed up {numimgs} files matching pattern')
    return numimgs


def backupFiles(flist, archbucket, target):
    s3 = boto3.client('s3')
    for fil in flist:
        localfile = os.path.join(target, fil)
        print(f'downloading {fil} to {localfile}')
        localdir, _ = os.path.split(localfile)
        os.makedirs(localdir, exist_ok=True)
        s3.download_file(archbucket, fil, localfile)
    return 


def processFolders(archbucket='ukmda-shared', targfldr='/data3/backups/ukmda', subfldr=None):
    s3 = boto3.client('s3')
    prefix = 'archive/'
    if subfldr:
        prefix = f'archive/{subfldr}'
    x = s3.list_objects_v2(Bucket=archbucket, Prefix=prefix, Delimiter='/')
    totalimgs = 0
    for pr in x['CommonPrefixes']: 
        pref = pr['Prefix']
        totalimgs += findFilesToBackup(archbucket, pref, targfldr)
    print(f'Backed up {totalimgs} in total')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage : python3 backupOldData.py /path/to/local [subfldr]')
        print('where')
        print('/path/to/local is the target location to create the backup at')
        print('subfldr is an optional subfolder to backup, for example "birmingham" would only backup that subfolder')
        exit(0)
    subfldr = None
    if len(sys.argv) > 2:
        subfldr = sys.argv[2]
    processFolders(targfldr=sys.argv[1], subfldr=subfldr)
