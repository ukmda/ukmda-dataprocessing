#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
from urllib.parse import unquote_plus


def copyFiles(s3bucket, s3object, target):
    s3 = boto3.resource('s3')
    x = s3object.find('FTPdetect')
    y = s3object.find('backup')
    z = s3object.find('detected')
    if x == -1 or y > 0 or z > 0:
        # its not an FTPdetect file so ignore it
        return 0
    
    ftpname = s3object[x:]
    bits = ftpname.split('_')
    mus = bits[4][:6]
    outdir = bits[1] + '_' + bits[2] + '_' + bits[3] + '_' + mus
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/' + ftpname
    
    s3object = unquote_plus(s3object)
    src = {'Bucket': s3bucket, 'Key': s3object}
    print(s3object)
    print(outf)
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    pth, _ = os.path.split(s3object)
    plap = pth +'/platepars_all_recalibrated.json'
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/platepars_all_recalibrated.json'
    src = {'Bucket': s3bucket, 'Key': plap}
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    s3c = boto3.client('s3')
    plap = pth +'/platepar_cmn2010.cal'
    response = s3c.head_object(Bucket=s3bucket, Key=plap)
    if response['ContentLength'] > 100: 
        outf = 'consolidated/platepars/' + bits[1] + '.json'
        src = {'Bucket': s3bucket, 'Key': plap}
        print(plap)
        print(outf)
        s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    return 0


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    target = 'ukmon-shared'

    copyFiles(s3bucket, s3object, target)
    return 0
