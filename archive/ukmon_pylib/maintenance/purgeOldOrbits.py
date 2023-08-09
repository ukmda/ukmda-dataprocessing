# copyright 2023- Mark McIntyre
# all rights reserved

import boto3
import sys


def findOrbitsToDelete(archbucket, location):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)
    print(f'clearing down images from {archbucket}/{location}... ', end='')
    sys.stdout.flush()
    files = [os.key for os in bucket.objects.filter(Prefix=location)]
    fltfiles = [file for file in files if '.pickle' not in file and 'report.txt' not in file and '.lst' not in file and file[-1] != '/']
    numimgs = len(fltfiles)
    deleteImages(fltfiles, archbucket)
    print(f'deleted {numimgs} files from {location}')
    return numimgs


def deleteImages(flist, archbucket):
    s3 = boto3.client('s3')
    chunk_size = 900
    chunked_list = [flist[i:i + chunk_size] for i in range(0, len(flist), chunk_size)]
    for ch in chunked_list:
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': k} for k in ch]
        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
    return 


def processFolders(archbucket, yr):
    s3 = boto3.client('s3')
    x = s3.list_objects_v2(Bucket=archbucket, Prefix=f'matches/{yr}/', Delimiter='/')
    totalimgs = 0
    for pr in x['CommonPrefixes']: 
        totalimgs += findOrbitsToDelete(archbucket, pr['Prefix'])
    print(f'purged {totalimgs} in total')


if __name__ == '__main__':
    processFolders(sys.argv[1], sys.argv[2])
