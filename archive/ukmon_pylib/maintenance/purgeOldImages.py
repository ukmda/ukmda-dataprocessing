# copyright 2023- Mark McIntyre
# all rights reserved

import boto3
import sys


def findImagesToDelete(archbucket, location):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)
    print(f'clearing down images from {archbucket}/{location}... ', end='')
    sys.stdout.flush()
    files = [os.key for os in bucket.objects.filter(Prefix=location)]
    fltfiles = [file for file in files if 'M20' in file or 'FF_' in file]
    imgfiles = [file for file in fltfiles if '.jpg' in file or '.mp4' in file]
    numimgs = len(imgfiles)
    deleteImages(imgfiles, archbucket)
    print(f'deleted {numimgs} images matching pattern')
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


def processFolders(archbucket):
    s3 = boto3.client('s3')
    x = s3.list_objects_v2(Bucket=archbucket, Prefix='archive/', Delimiter='/')
    totalimgs = 0
    for pr in x['CommonPrefixes']: 
        totalimgs += findImagesToDelete(archbucket, pr['Prefix'])
    print(f'purged {totalimgs} in total')


if __name__ == '__main__':
    processFolders(sys.argv[1])
