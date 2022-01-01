#
# lambda function to be triggered when a jpg file arrives in ukmon-shared
# to copy it to the archive website
#
import boto3
import os
import sys
from urllib.parse import unquote_plus


def copyJpgToArchive(s3bucket, s3object):
    s3 = boto3.resource('s3')
    try:
        target = os.environ['WEBSITEBUCKET']
        target = target[5:]
    except Exception:
        target = 'mjmm-ukmonarchive.co.uk'

    x = s3object.find('M20')
    if x == -1: 
        y = s3object.find('FF_')
        if y == -1:
            y = s3object.find('_stack_')
            if y == -1:
                # its not an interesting file
                return 
            else:
                # its the stack file
                statid = os.path.basename(s3object)[0:6]
                if statid[0] == '.': 
                    statid = os.path.basename(s3object)[2:8]
                outf = 'latest/{:s}.jpg'.format(statid)
                s3object = unquote_plus(s3object)
                src = {'Bucket': s3bucket, 'Key': s3object}
                print(s3object, outf)
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="image/jpg", MetadataDirective='REPLACE')
                return 
        else:
            # its an RMS file probably
            yr = s3object[y+10:y+14]
            ym = s3object[y+10:y+16]
            outf = 'img/single/{:s}/{:s}/'.format(yr, ym) + s3object[y:]
    else:
        # its a UFO file
        yr = s3object[x+1:x+5]
        ym = s3object[x+1:x+7]
        outf = 'img/single/{:s}/{:s}/'.format(yr, ym) + s3object[x:]

    s3object = unquote_plus(s3object)
    src = {'Bucket': s3bucket, 'Key': s3object}
    print(s3object, outf)
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="image/jpeg", MetadataDirective='REPLACE')
    return


def lambda_handler(event, context):

    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    copyJpgToArchive(s3bucket, s3object)


if __name__ == "__main__":
    s3bucket = 'ukmon-shared'
    s3object = 'archive/Cardiff/Cardiff_Camera_1/2015/201510/20151025/M20151026_030101_MC1_c1P.jpg'
    if len(sys.argv) > 0:
        fname = sys.argv[1]
        if './' in fname:
            s3object = 'archive/' + fname[2:]
        else:
            s3object = 'archive/' + fname
    #print(s3object)
    copyJpgToArchive(s3bucket, s3object)
