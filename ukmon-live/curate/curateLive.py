# script to curate UKMON live data as it arrives
# note: requires Python 3.7 at present
# note: see instructions at end of file on how to build and deploy

import os
import boto3
from urllib.parse import unquote_plus
import curateEngine as ce
import numpy as np
Polynomial = np.polynomial.Polynomial


def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    record = event['Records'][0]
    s3object = record['s3']['object']['key']

    ce.MAXRMS = float(os.environ['MAXRMS'])  # max deviation from straight
    ce.MINLEN = float(os.environ['MINLEN'])  # min path length to consider
    ce.MAXLEN = float(os.environ['MAXLEN'])  # max path length to consider
    ce.MAXBRI = float(os.environ['MAXBRI'])  # max brightness after which all events are kept
    ce.MAXOBJS = int(os.environ['MAXOBJ'])  # too many objects in the detection
    ce.MAXGAP = int(os.environ['MAXGAP'])  # 1.5 seconds gap in a trail
    usf = os.environ['SUBFOL']  # use subfolders for bad files
    deb = os.environ['DEBUG']   # enable debugging

    useSubfolders = True
    if usf in ['False', 'FALSE', 'false']:
        useSubfolders = False

    ce.debug = False
    if deb in ['True', 'TRUE', 'true']:
        ce.debug = True

    logname = 'LiveMon: '

    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        target = 'mjmm-live'
    else:
        target = 'ukmon-live'

    x = s3object.find('xml')
    if x > 0:
        s3object = unquote_plus(s3object)
        x = s3object.find('UK00')
        if x > 0:
            print(logname, s3object, ' skipping RMS files for now')
            return 0

        xmlname = '/tmp/' + s3object
        s3.meta.client.download_file(target, s3object, xmlname)

        sts, msg, nobjs, maxbri, gtp, tottotpx = ce.CheckifValidMeteor(xmlname)
        msg = msg + ',{:d},{:d}, {:d}'.format(nobjs, int(maxbri), int(tottotpx))
        print(logname, msg)

        if sts is False:
            # move the files to a holding area on ukmon-shared in case we need them back
            if useSubfolders is True:
                typ = msg.split(',')[0]

            archbucket = 'ukmon-shared'
            try:
                copy_source = {'Bucket': target, 'Key': s3object}
                archname = 'live-bad-files/' + typ + '/' + s3object
                s3.meta.client.copy(CopySource=copy_source, Bucket=archbucket, Key=archname)
                s3.meta.client.delete_object(Bucket=target, Key=s3object)
                print(logname, s3object, ' moved')
            except:
                print(logname, s3object, ' removing the xml file failed!')

            obl = len(s3object)
            jpgname = s3object[:obl - 4] + 'P.jpg'
            try:
                copy_source = {'Bucket': target, 'Key': jpgname}
                archname = 'live-bad-files/' + typ + '/' + jpgname
                s3.meta.client.copy(CopySource=copy_source, Bucket=archbucket, Key=archname)
                s3.meta.client.delete_object(Bucket=target, Key=jpgname)
                print(logname, jpgname, ' moved')
            except:
                print(logname, jpgname, ' removing the jpg file failed!')
            jpgname = s3object[:obl - 4] + '.mp4'
            try:
                copy_source = {'Bucket': target, 'Key': jpgname}
                archname = 'live-bad-files/' + typ + '/' + jpgname
                s3.meta.client.copy(CopySource=copy_source, Bucket=archbucket, Key=archname)
                s3.meta.client.delete_object(Bucket=target, Key=jpgname)
                print(logname, jpgname, ' moved')
            except:
                print(logname, jpgname, ' no mp4 found')
        # clean up local filesystem
        os.remove(xmlname)
    return 0


"""
building a compatible numpy.
 on an amazon linux machine, create a folder and chdir into it then
 install pytz and numpy locally along with the xmldict, ReadUFO and curate files

 pip3 install -t. pytz
 pip3 install -t. numpy

 remove the dist-info and pycache folders
 find . -name __pycache__ -exec rm -Rf {} \\;
 rm -Rf *.dist-info

 then create a zip file
 zip -r function.zip .

 the zip file can be copied to a Windows PC or deployed directly with
 aws lambda update-function-code --function-name MonitorLiveFeed --zip-file fileb://function.zip
"""
