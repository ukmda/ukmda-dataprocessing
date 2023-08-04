# Copyright (C) 2018-2023 Mark McIntyre
#
# lambda function to be triggered when a jpg file arrives in the shared bucket
# to copy it to the archive website
#
import boto3
import os
import sys
from urllib.parse import unquote_plus


def copyKmlToWebsite(s3bucket, s3object):
    s3 = boto3.resource('s3')
    target = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')[5:]

    x = s3object.find('.kml')
    if x == -1: 
        # its not a kml file - should be impossible to get here
        return 
    else:
        src = {'Bucket': s3bucket, 'Key': s3object}
        s3object = unquote_plus(s3object)
        _, kmlname = os.path.split(s3object)
        outf = 'img/kmls/{:s}'.format(kmlname)
        #print(s3object, outf, target)
        s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="application/vnd.google-earth.kml+xml", MetadataDirective='REPLACE')
        outf2 = f'kmls/{kmlname}'
        shbuck = os.getenv('SHAREDBUCKET', default='s3://ukmda-shared')[5:]
        s3.meta.client.copy_object(Bucket=shbuck, Key=outf2, CopySource=src, ContentType="application/vnd.google-earth.kml+xml", MetadataDirective='REPLACE')
        return 


def lambda_handler(event, context):

    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    copyKmlToWebsite(s3bucket, s3object)


if __name__ == "__main__":
    s3bucket = os.getenv('SHAREDBUCKET', default='ukmda-shared')[5:]
    s3object = 'archive/Tackley/UK0006/2021/202108/20210828/UK0006-25km.kml'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if './' in fname:
            s3object = 'archive/' + fname[2:]
        else:
            s3object = 'archive/' + fname
    #print(s3object)
    copyKmlToWebsite(s3bucket, s3object)
