#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
from urllib.parse import unquote_plus


def copyFiles(s3bucket, s3object, target, maxdetcount):
    s3 = boto3.resource('s3')
    x = s3object.find('FTPdetect')
    y = s3object.find('backup')
    z = s3object.find('detected')
    if x == -1 or y > 0 or z > 0:
        # its not a calibrated FTPdetect file so ignore it
        return 0
    
    ftpname = s3object[x:]

    bits = ftpname.split('_')
    mus = bits[4][:6]
    outdir = bits[1] + '_' + bits[2] + '_' + bits[3] + '_' + mus
    if bits[-1] == 'manual.txt':
        outdir = outdir + '_man'
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/' + ftpname

    s3object = unquote_plus(s3object)

    # check for too many events to be realistic data
    s3.meta.client.download_file(s3bucket, s3object, '/tmp/tmp.txt')
    with open('/tmp/tmp.txt') as inf:
        li = inf.readline().strip()
    metcount = int(li.split(' ')[3])
    if metcount > maxdetcount:
        _, fn = os.path.split(s3object)
        print('too many events ({}) in {}'.format(metcount, fn))
        return 0

    src = {'Bucket': s3bucket, 'Key': s3object}
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    s3c = boto3.client('s3')
    pth, _ = os.path.split(s3object)
    plap = pth +'/platepars_all_recalibrated.json'
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/platepars_all_recalibrated.json'
    src = {'Bucket': s3bucket, 'Key': plap}
    try:
        response = s3c.head_object(Bucket=s3bucket, Key=plap)
        if response['ContentLength'] > 100: 
            s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
    except:
        print(f'platepars_all is missing for {pth}')

    pth, _ = os.path.split(s3object)
    plap = pth +'/.config'
    try:
        response = s3c.head_object(Bucket=s3bucket, Key=plap)
        if response['ContentLength'] > 100: 
            outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/.config'
            src = {'Bucket': s3bucket, 'Key': plap}
            s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
    except:
        print(f'config is missing for {pth}')

    try:
        plap = pth +'/platepar_cmn2010.cal'
        response = s3c.head_object(Bucket=s3bucket, Key=plap)
        if response['ContentLength'] > 100: 
            outf = 'consolidated/platepars/' + bits[1] + '.json'
            src = {'Bucket': s3bucket, 'Key': plap}
            s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
    except:
        print(f'platepar missing for {pth}')

    return 0


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    target = 'ukmon-shared'

    maxdetcount = 500
    copyFiles(s3bucket, s3object, target, maxdetcount)
    return 0
