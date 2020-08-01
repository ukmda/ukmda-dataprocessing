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
MAXRMS=1.5
MINLEN=4 # very short trails are statistically unreliable
MAXLEN=80 # 80 frames is about 1.5 seconds video
MAXOBJS=20
MAXGAP=75 # corresponds to 1.5 seconds gap in the meteor trail

def monotonic(x):
    dx = np.diff(x)
    return np.all(dx <= 0) or np.all(dx >= 0)

def CheckifValidMeteor(xmlname, target):
    # initialise fit variables

    dd=ReadUFOCapXML.UCXml(xmlname)
    fps, cx, cy = dd.getCameraDetails()
    nobjs, objlist = dd.getNumObjs()
    isgood=0
    _,fname=os.path.split(xmlname)

    if nobjs==0:
        print('{:s}, nopaths, 0, 0.0, 0, 0, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, 0, 0'.format(fname))
        return False

    if nobjs>MAXOBJS:
        print('{:s}, manyobjs, 0, 0.0, 0, 0, 0.00, 0.00, 0.00, 0.00, 0, {:d}, 0, 0, 0'.format(fname, nobjs))
        return False

    tottotpx=0
    for i in range(nobjs):
        pathx, pathy, bri, pxls, fnos = dd.getPathv2(objlist[i])
        totpx=int(sum(pxls))
        tottotpx = tottotpx + totpx
        res, msg= CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos)
        isgood = isgood + res
        maxbri=int(max(bri))
        print('{:s}, {:s}, {:d}, {:d}, {:d}, {:d}'.format(fname, msg, nobjs, maxbri, totpx, tottotpx))
        
    if isgood == 0:    
        return False
    else:
        return True

def leastsq1(x, y):
    a = np.vstack([x, np.ones(len(x))]).T
    return np.dot(np.linalg.inv(np.dot(a.T, a)), np.dot(a.T, y))
    
def CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos):
    dist=0
    app_m=0
    m=0
    ym=0
    xm=0
    vel=0
    rms=0

    # we expect meteor paths to be monotonic in X or Y or both
    # A path that darts about is unlikely to be analysable
    badline=False
    if  monotonic(pathx)==False and  monotonic(pathy) == False:
        badline=True
    plen=len(pathx)
    maxg=0
    if plen > 1:
        maxg=int(max(np.diff(fnos)))
        if maxg > MAXGAP:
            badline=True

    # very short paths are stasticially unreliable
    # very long paths are unrealistic as meteors pretty quick events
    if plen >= MINLEN and plen <=MAXLEN:
        try:
            cmin, cmax = min(pathx), max(pathx)
            pfit, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
                domain=(cmin, cmax))
            _, m = pfit
            if (pathx[-1]-pathx[0]) !=0:
                app_m = (pathy[-1]-pathy[0])/(pathx[-1]-pathx[0])
            resid, _, _, _ = stats
            rms = np.sqrt(resid[0]/len(pathx))

            # if the line is nearly vertical, a fit of y wil be a poor estimate
            # so before discarding the data, try swapping the axes
            if rms > MAXRMS:
                cmin, cmax = min(pathy), max(pathy)
                pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                    domain=(cmin, cmax))
                _, m = pfit
                resid, _, _, _ = stats
                rms2 = np.sqrt(resid[0]/len(pathy))
                if (pathy[-1]-pathy[0]) != 0:
                    app_m = (pathx[-1]-pathx[0])/(pathy[-1]-pathy[0])
                rms2 = min(rms2, rms)
                rms = min(rms2,rms)
        except:
            msg='fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg

        # work out the length of the line; very short lines are statistically unreliable
        p1=np.c_[pathx[0],pathy[0]]
        p2=np.c_[pathx[-1],pathy[-1]]
        dist=np.linalg.norm(p2-p1)
        vel=dist*2*fps/plen
        # very low RMS is improbable but lets allow it for now
        if rms > MAXRMS :
            msg='plane, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg
            #ShowGraph(fname, pathx, pathy, A0, m, msg)
        else:
            xm = int(max(pathx))
            if xm > cx/2:
                xm = int(min(pathx))
            ym = int(min(pathy))
            if ym > cy/2:
                ym = int(min(pathy))
            if dist < 10 and vel < 100 :
                msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                return 0, msg
            else:
                if badline == True: 
                    msg='badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    return 0, msg
                else:
                    msg='meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    return 1, msg
    else:
        if badline==True:
            msg='badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel, maxg)
        else:
            if plen < MINLEN:
                msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel, maxg)
            else:
                msg='toolong, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel, maxg)
        return 0, msg
    msg='flash, {:d}, 0.0, 0, 0, 0.00, 0.00, 0.00, 0.00, {:d}'.format(len(pathx), maxg)
    return 0, msg


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
                print(logname, s3object, ' moved')
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
                print(logname, jpgname, ' moved')
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
