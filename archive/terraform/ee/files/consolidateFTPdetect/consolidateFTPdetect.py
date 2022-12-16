#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
from urllib.parse import unquote_plus
import time


def copyFiles(s3bucket, s3object, target, maxdetcount):
    s3 = boto3.resource('s3')
#    x = s3object.find('FTPdetect')
#    y = s3object.find('backup')
#    z = s3object.find('detected')

    if 'FTPdetectinfo' not in s3object or 'backup' in s3object or 'detected' in s3object \
            or 'uncalibrated' in s3object: 
        # its not a calibrated FTPdetect file so ignore it
        print(f'not a relevant file {s3object}')
        return 0
    
    _, ftpname = os.path.split(s3object)

    bits = ftpname.split('_')
    mus = bits[4][:6]
    outdir = bits[1] + '_' + bits[2] + '_' + bits[3] + '_' + mus
    if bits[-1] == 'manual.txt':
        outdir = outdir + '_man'
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/' + ftpname

    s3object = unquote_plus(s3object)

    # check for too many events to be realistic data
    s3.meta.client.download_file(s3bucket, s3object, '/tmp/tmp.txt')
    metcount = 0
    recal = False
    with open('/tmp/tmp.txt') as inf:
        lis = inf.readlines()
    if len(lis) == 0:
        print('missing content in FTP file')
        return 0
    metcount = int(lis[0].strip().split()[3])
    if metcount > maxdetcount:
        _, fn = os.path.split(s3object)
        print('too many events ({}) in {}'.format(metcount, fn))
        return 0
    # check data recalibrated 
    for li in lis:
        if 'Recalibrated' in li:
            recal = True
            break
    
    s3c = boto3.client('s3')
    pth, _ = os.path.split(s3object)

    # only copy the platepar if some data was recalibrated
    if recal is True:
        plap = pth +'/platepars_all_recalibrated.json'
        outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/platepars_all_recalibrated.json'
        src = {'Bucket': s3bucket, 'Key': plap}

        # loop to allow for platepar and config being uploaded after the Lambda triggers
        for i in range(11):
            try:
                response = s3c.head_object(Bucket=s3bucket, Key=plap)
                if response['ContentLength'] > 100: 
                    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
                break
            except:
                time.sleep(1)
        if i == 10 and recal is True:
            print(f'platepars_all is missing for {pth}')

    cfgf = pth +'/.config'
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/.config'
    src = {'Bucket': s3bucket, 'Key': cfgf}
    for i in range(11):
        try:
            response = s3c.head_object(Bucket=s3bucket, Key=cfgf)
            if response['ContentLength'] > 100: 
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
            break
        except:
            time.sleep(1)
    if i == 10 and recal is True:
        print(f'config is missing for {pth}')

    plas = pth +'/platepar_cmn2010.cal'
    outf = 'consolidated/platepars/' + bits[1] + '.json'
    src = {'Bucket': s3bucket, 'Key': plas}
    for i in range(11):
        try:
            response = s3c.head_object(Bucket=s3bucket, Key=plas)
            if response['ContentLength'] > 100: 
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
            break
        except:
            time.sleep(1)
    if i == 10 and recal is True:
        print(f'platepar missing for {pth}')

    # copy FTP file last as its the trigger for further Lambdas
    outf = 'matches/RMSCorrelate/' + bits[1] + '/' + outdir + '/' + ftpname    
    src = {'Bucket': s3bucket, 'Key': s3object}
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    return 0


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    target = 'ukmon-shared'

    maxdetcount = int(os.getenv('MAXDETS', default=750))
    copyFiles(s3bucket, s3object, target, maxdetcount)
    return 0
