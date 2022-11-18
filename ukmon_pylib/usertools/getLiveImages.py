#
# python script to get all live JPGs for a specified time
#
import os
import sys
import boto3
import tempfile


def getLiveJpgs(dtstr):
    tmppth = tempfile.mkdtemp()
    s3 = boto3.client('s3')
    buck = os.getenv('UKMONLIVEBUCKET', default='s3://ukmon-live')[5:]
    x = s3.list_objects_v2(Bucket=buck,Prefix=f'M{dtstr}')
    if  x['KeyCount'] > 0:
        print(f"found {x['KeyCount']} records, saving to {tmppth}")
        for k in x['Contents']:
            key = k['Key']
            if '.jpg' in key:
                print(key)
                s3.download_file(buck, key, os.path.join(tmppth, key))
    else:
        print('no records found')

if __name__ == '__main__':
    getLiveJpgs(sys.argv[1])
