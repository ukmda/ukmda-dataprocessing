#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
from urllib.parse import unquote_plus


# add a row to the CamTimings table
def addRowCamTimings(s3bucket, s3object, ftpname):
    s3c = boto3.client('s3')
    dtstamp = s3c.head_object(Bucket=s3bucket, Key=s3object)['LastModified']
    ddb = boto3.resource('dynamodb', region_name='eu-west-1') 
    table = ddb.Table('ukmon_uploadtimes')
    spls = ftpname.split('_')
#    print(spls[0], dtstamp)
    if spls[-1] == 'manual.txt':
        manflag = '_man'
        manual = True
    else:
        manflag = ''
        manual = False
    uploaddate = dtstamp.strftime('%Y%m%d')
    uploadtime = dtstamp.strftime('%H%M%S')
    table.put_item(
        Item={
            'stationid': spls[0],
            'dtstamp': uploaddate + '_' + uploadtime + manflag,
            'uploaddate': int(uploaddate),
            'uploadtime': int(uploadtime),
            'manual': manual
        }
    )   
    print(spls[0], uploaddate)
    return 


def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    target = 'ukmon-shared'

    _, fname = os.path.split(s3object)
    #x = s3object.find('M20')
    #if x == -1:
    if fname[:3] !='M20':
        # its not a standard ufoa file, check if its an rms file
        x = fname.find('_20')
        if x == -1:
            # yep not interested
            return 0

    outf = 'consolidated/temp/' + fname
    s3object = unquote_plus(s3object)
    print(s3object)
    print(outf)
    src = {'Bucket': s3bucket, 'Key': s3object}
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    _, fname = os.path.split(s3object)
    try:
        addRowCamTimings(s3bucket, s3object, fname)
    except Exception:
        pass
    return 0
