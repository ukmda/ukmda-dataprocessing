# copyright 2023- Mark McIntyre
# all rights reserved

import boto3
import sys


def findCsvsToDelete(archbucket, pref):
    s3 = boto3.resource('s3')
    s3c = boto3.client('s3')
    bucket = s3.Bucket(archbucket)
    patt = f'matches/single/rawcsvs/{pref}'
    print(f'clearing down empty csvs from {archbucket}/{patt}... ', end='')
    files = [obj.key for obj in bucket.objects.filter(Prefix=patt)]
    filestodel = []
    for fil in files:
        response = s3c.head_object(Bucket=archbucket, Key=fil)
        size = response['ContentLength']
        if size < 100:
            filestodel.append(fil)
    numimgs = len(filestodel)
    deleteZeroSizeFiles(filestodel, archbucket)
    print(f'deleted {numimgs} empty CSVs')
    return numimgs


def deleteZeroSizeFiles(flist, archbucket):
    s3 = boto3.client('s3')
    chunk_size = 900
    chunked_list = [flist[i:i + chunk_size] for i in range(0, len(flist), chunk_size)]
    for ch in chunked_list:
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': k} for k in ch]
        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
    return 


if __name__ == '__main__':
    findCsvsToDelete('ukmda-shared', sys.argv[1])
