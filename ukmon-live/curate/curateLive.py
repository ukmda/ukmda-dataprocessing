# script to curate UKMON live data as it arrives
# note: requires Python 3.7 at present
# note: see instructions at end of file on how to build and deploy

import os, sys 
import datetime, math
import boto3
import botocore
from urllib.parse import unquote_plus
import ReadUFOCapXML
import numpy as np
Polynomial = np.polynomial.Polynomial

logname='LiveMon: '

def monotonic(x):
    dx = np.diff(x)
    return np.all(dx <= 0) or np.all(dx >= 0)

def CheckifValidMeteor(xmlname, target):
    # initialise fit variables
    dist=0
    app_m=0
    m=0
    ym=0
    xm=0
    vel=0
    rms=0
    maxrms=1

    dd=ReadUFOCapXML.UCXml(xmlname)
    fps, cx, cy = dd.getCameraDetails()
    pathx, pathy, _ = dd.getPath()
    _,fname=os.path.split(xmlname)

    # we expect meteor paths to be monotonic in X or Y or both
    # A path that darts about is unlikely to be analysable
    if  monotonic(pathx)==False and  monotonic(pathy) == False:
        msg='erratic, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
        print (logname, fname, msg )
        return False

    # RMS ignores paths of less than 6 frames
    # lets try with 4 for now
    l=len(pathx)
    if l < 4 :
        msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
        print (logname, fname, msg )
        return False

    try:
        cmin, cmax = min(pathx), max(pathx)
        pfit, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
            domain=(cmin, cmax))
        _, m = pfit
        app_m = (pathy[-1]-pathy[0])/(pathx[-1]-pathx[0])
        resid, _, _, _ = stats
        rms = np.sqrt(resid[0]/len(pathx))
        # if the line is nearly vertical, a fit of y wil be a poor estimate
        # so before discarding the data, try swapping the axes
        if rms > maxrms:
            cmin, cmax = min(pathy), max(pathy)
            pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                domain=(cmin, cmax))
            _, m = pfit
            resid, _, _, _ = stats
            rms = np.sqrt(resid[0]/len(pathy))
            app_m = (pathx[-1]-pathx[0])/(pathy[-1]-pathy[0])

    except:
        msg='fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
        print(logname, fname, msg)
        return False

    # work out the length of the line; very short lines are statistically unreliable
    p1=np.c_[pathx[0],pathy[0]]
    p2=np.c_[pathx[-1],pathy[-1]]
    dist=np.linalg.norm(p2-p1)
    vel=dist*2*fps/l

    # very low RMS is improbable but lets allow it for now
    if rms > maxrms :
        msg='plane, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
        print (logname, fname, msg )
        return False
    else:
        xm = int(max(pathx))
        if xm > cx/2:
            xm = int(min(pathx))
        ym = int(min(pathy))
        if ym > cy/2:
            ym = int(min(pathy))
        if dist < 5 :
            msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
            print (logname, fname, msg )
            return False

        msg='meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
        print (logname, fname, msg)
        return True

def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    record = event['Records'][0]
    s3object = record['s3']['object']['key']

    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    #print(response)
    if response == '317976261112':
        target = 'mjmm-live'
    else:
        target = 'ukmon-live'

    x=s3object.find('xml')
    if x > 0:
        s3object = unquote_plus(s3object)
        x = s3object.find('UK00')
        if x > 0 :
            print(logname,s3object, ' skipping RMS files for now')
            return 0

        xmlname = '/tmp/' + s3object
        s3.meta.client.download_file(target, s3object, xmlname) 

        if CheckifValidMeteor(xmlname, target)==False:
            # move the files to a holding area on ukmon-shared in case we need them back
            archbucket='ukmon-shared'
            try: 
                copy_source={'Bucket': target, 'Key': s3object}   
                archname='live-bad-files/'+s3object
                s3.meta.client.copy(CopySource=copy_source, Bucket=archbucket, Key=archname)
                s3.meta.client.delete_object(Bucket=target, Key=s3object)
            except:
                print(logname, s3object,' removing the xml file failed!')

            l=len(s3object)
            jpgname=s3object[:l-4]+'P.jpg'
            #print('delete ', jpgname)
            try: 
                copy_source={'Bucket': target, 'Key': jpgname}   
                archname='live-bad-files/'+jpgname
                s3.meta.client.copy(CopySource=copy_source, Bucket=archbucket, Key=archname)
                s3.meta.client.delete_object(Bucket=target, Key=jpgname)
            except:
                print(logname, jpgname, ' removing the jpg file failed!')
        # clean up local filesystem
        os.remove(xmlname)
    
    return 0

# building a compatible numpy.
# on an amazon linux machine, create a folder and chdir into it then 
# install pytz and numpy locally along with the xmldict, ReadUFO and curate files
# 
# pip3 install -t. pytz
# pip3 install -t. numpy
#
# remove the dist-info and pycache folders
# find . -name __pycache__ -exec rm -Rf {} \;
# rm -Rf *.dist-info
# 
# then create a zip file 
# zip -r function.zip .
# 
# the zip file can be copied to a Windows PC or deployed directly with
# aws lambda update-function-code --function-name MonitorLiveFeed --zip-file fileb://function.zip
