# Copyright (C) 2018-2023 Mark McIntyre
import urllib.parse
import boto3
import os
import sys
import shutil
import json
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

from wmpl.Utils.Pickling import loadPickle
from pickleAnalysis import createAdditionalOutput
from createOrbitPageIndex import createOrbitPageIndex


def findSite(stationid, ddb):
    table = ddb.Table('ukmon_camdetails')
    response = table.query(KeyConditionExpression=Key('stationid').eq(stationid))
    try:
        items = response['Items']
        if len(items) > 0:
            return items[0]['site']
        else:
            return None
    except Exception:
        print('record not found')
    return None


def generateExtraFiles(key, archbucket, websitebucket, ddb, s3):
    fuloutdir, fname = os.path.split(key)
    _, orbname = os.path.split(fuloutdir)
    tmpdir = os.getenv('TMP', default='/tmp')

    yr = orbname[:4]
    ym = orbname[:6]
    ymd= orbname[:8]
    webpth = f'reports/{yr}/orbits/{ym}/{ymd}/{orbname}/'
        
    outdir = os.path.join(tmpdir, orbname)
    try: 
        os.makedirs(outdir, exist_ok=True)
        locfname = os.path.join(outdir, fname)

        s3.meta.client.download_file(archbucket, key, locfname)
        traj = loadPickle(outdir, fname)
        traj.save_results = True

        #print('loaded pickle')
        createAdditionalOutput(traj, outdir)
        #print('created additional output')
        # file to write JPGs html to, for performance benefits
        jpghtml = open(os.path.join(outdir, 'jpgs.html'), 'w')
        mp4html = open(os.path.join(outdir, 'mpgs.html'), 'w')
        # loop over observations adding jpgs to the listing file
        jpgf = open(os.path.join(outdir, 'jpgs.lst'), 'w')
        mp4f = open(os.path.join(outdir, 'mpgs.lst'), 'w')
        #print('opened image list files')
        for obs in traj.observations:
            js = json.loads(obs.comment)
            ffname = js['ff_name']
            # case when filename is nonstandard 
            if 'FF_' not in ffname and 'FR_' not in ffname:
                ffname = 'FF_' + ffname
            ffname = ffname.replace('FR_', 'FF_').replace('.bin', '.fits')
            if '.bin' not in ffname and '.fits' not in ffname:
                ffname = ffname + '.fits'
                
            spls = ffname.split('_')
            id = spls[1]
            dtstr = spls[2]
            tmstr = spls[3]
            jpgname=f'img/single/{dtstr[:4]}/{dtstr[:6]}/{ffname}'.replace('fits','jpg')
            mp4name=f'img/mp4/{dtstr[:4]}/{dtstr[:6]}/{ffname}'.replace('fits','mp4')

            res = s3.meta.client.list_objects_v2(Bucket=websitebucket,Prefix=jpgname)
            if res['KeyCount'] > 0:
                jpgf.write(f'{jpgname}\n')
                jpghtml.write(f'<a href="/{jpgname}"><img src="/{jpgname}" width="20%"></a>\n')
            else:
                print(f'{jpgname} not found')
            res = s3.meta.client.list_objects_v2(Bucket=websitebucket,Prefix=mp4name)
            if res['KeyCount'] > 0:
                mp4f.write(f'{mp4name}\n')
                mp4html.write(f'<a href="/{mp4name}"><video width="20%"><source src="/{mp4name}" width="20%" type="video/mp4"></video></a>\n')
            else:
                print(f'{mp4name} not found')
            site = findSite(id, ddb)
            if site is not None:
                fldr = site + '/' + id
                evtdtval = datetime.strptime(f'{dtstr}_{tmstr}', '%Y%m%d_%H%M%S')
                if evtdtval.hour < 13:
                    evtdtval = evtdtval + timedelta(days = -1)
                    dtstr = evtdtval.strftime('%Y%m%d')
                findOtherFiles(dtstr, archbucket, websitebucket, outdir, fldr, s3)

        jpghtml.close()
        mp4html.close()
        jpgf.close()
        mp4f.close()
        #print('created image lists')
        repfname = locfname.replace('trajectory.pickle', 'report.txt')
        key2 = key.replace('trajectory.pickle', 'report.txt')
        s3.meta.client.download_file(archbucket, key2, repfname)

        key2 = webpth + 'extrajpgs.html'
        locfname = os.path.join(outdir, 'extrajpgs.html')
        try:
            s3.meta.client.download_file(websitebucket, key2, locfname)
        except:
            print('no extrajpgs.html')
            pass
        key2 = webpth + 'extrampgs.html'
        locfname = os.path.join(outdir, 'extrampgs.html')
        try:
            s3.meta.client.download_file(websitebucket, key2, locfname)
        except:
            print('no extrampgs.html')
            pass

        # pushFilesBack creates the zipfile so we need to do this first
        pushFilesBack(outdir, archbucket, websitebucket, fuloutdir, s3)
        createOrbitPageIndex(outdir, websitebucket, s3)

        idxname = os.path.join(outdir, 'index.html')
        key = os.path.join(webpth, 'index.html')
        extraargs = getExtraArgs('index.html')
        s3.meta.client.upload_file(idxname, websitebucket, key, ExtraArgs=extraargs) 
        #print('pushing to website')
        #pushToWebsite(archbucket, fuloutdir, websitebucket, orbname, s3)
    except:
        print(f'problem processing {orbname}')
    try:
        shutil.rmtree(outdir)
    except Exception:
        print(f'unable to remove {outdir}')
    return 


def findOtherFiles(evtdt, archbucket, websitebucket, outdir, fldr, s3):

    thispth = f'archive/{fldr}/{evtdt[:4]}/{evtdt[:6]}/{evtdt[:8]}/'
    print(f'looking in {thispth}')
    corrpth = ''
    objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=thispth)
    if objlist['KeyCount'] > 0:
        keys = objlist['Contents']
        for k in keys:
            fname = k['Key']
            #print(f'fname is {fname}')
            if 'fieldsums' in fname or 'radiants' in fname or '.csv' in fname:
                _, corrpth = os.path.split(fname)
            if '.csv' in fname or '.kml' in fname or 'FTPdetectinfo' in fname:
                _, locfname = os.path.split(fname)
                locfname = os.path.join(outdir, locfname)
                s3.meta.client.download_file(archbucket, fname, locfname)
    while objlist['IsTruncated'] is True:
        contToken = objlist['NextContinuationToken'] 
        objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=thispth, ContinuationToken=contToken)
        if objlist['KeyCount'] > 0:
            keys = objlist['Contents']
            for k in keys:
                fname = k['Key']
                #print(f'fname is {fname}')
                if 'fieldsums' in fname or 'radiants' in fname or '.csv' in fname:
                    _, corrpth = os.path.split(fname)
            if '.csv' in fname or '.kml' in fname or 'FTPdetectinfo' in fname:
                _, locfname = os.path.split(fname)
                locfname = os.path.join(outdir, locfname)
                s3.meta.client.download_file(archbucket, fname, locfname)

    if len(corrpth) > 30:
        corrpth = corrpth[:29]
        statid = corrpth[:6]
        for kml in ('25km.kml', '70km.kml', '100km.kml'):
            fname = f'img/kmls/{statid}-{kml}'
            locfname = os.path.join(outdir, f'{statid}-{kml}')
            try:
                s3.meta.client.download_file(websitebucket, fname, locfname)
            except:
                print(f'unable to collect {fname}')

        thispth = f'matches/RMSCorrelate/{statid}/{corrpth}'
        ftpf = f'{thispth}/FTPdetectinfo_{corrpth}.txt'
        locfname = os.path.join(outdir, f'FTPdetectinfo_{corrpth}.txt')
        try:
            s3.meta.client.download_file(archbucket, ftpf, locfname)
        except:
            print(f'unable to collect {ftpf}')

        ppf = f'{thispth}/platepars_all_recalibrated.json'
        locfname = os.path.join(outdir, f'{statid}_platepars_all_recalibrated.json')
        try:
            s3.meta.client.download_file(archbucket, ppf, locfname)
        except:
            print(f'unable to collect {ppf}')
    else:
        print('unable to locate ftp, platepar or kmls')
    return


def pushFilesBack(outdir, archbucket, websitebucket, fldr, s3):
    # get filelist before creating the zipfile! 
    flist = os.listdir(outdir)

    _, pth =os.path.split(outdir)
    yr = pth[:4]
    ym = pth[:6]
    ymd= pth[:8]
    webpth = f'reports/{yr}/orbits/{ym}/{ymd}/{pth}/'

    zipfname = os.path.join(outdir, pth +'.zip')
    zipf = ZipFile(zipfname, 'w', compression=ZIP_DEFLATED, compresslevel=9)

    for f in flist:
        #print(f)
        locfname = os.path.join(outdir, f)
        zipf.write(locfname)
        # some files need to be pushed to the website, some to the archive bucket
        if '3dtrack' in f or '2dtrack' in f:
            key = os.path.join(webpth, f)
            extraargs = getExtraArgs(locfname)
            s3.meta.client.upload_file(locfname, websitebucket, key, ExtraArgs=extraargs)
        elif '.lst' in f:
            key = os.path.join(f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{pth}', f)
            extraargs = getExtraArgs(locfname)
            s3.meta.client.upload_file(locfname, archbucket, key, ExtraArgs=extraargs)
        elif 'summary' in f:
            key = os.path.join(fldr, f)
            # print(locfname, key)
            extraargs = getExtraArgs(locfname)
            s3.meta.client.upload_file(locfname, archbucket, key, ExtraArgs=extraargs)
        elif 'orbit_full.csv' in f:
            key = os.path.join(f'matches/{yr}/fullcsv', f)
            extraargs = getExtraArgs(locfname)
            s3.meta.client.upload_file(locfname, archbucket, key, ExtraArgs=extraargs)

    zipf.close()
    # now we push the zipfile
    key = os.path.join(webpth, pth + '.zip')
    extraargs = getExtraArgs(zipfname)
    s3.meta.client.upload_file(zipfname, websitebucket, key, ExtraArgs=extraargs) 
    return 


def getExtraArgs(fname):
    _, file_ext = os.path.splitext(fname)
    ctyp='text/plain'
    if file_ext=='.jpg': 
        ctyp = 'image/jpeg'
    if file_ext=='.fits': 
        ctyp = 'image/fits'
    elif file_ext=='.png': 
        ctyp = 'image/png'
    elif file_ext=='.bmp': 
        ctyp = 'image/bmp'
    elif file_ext=='.mp4': 
        ctyp = 'video/mp4'
    elif file_ext=='.csv': 
        ctyp = 'text/csv'
    elif file_ext=='.html': 
        ctyp = 'text/html'
    elif file_ext=='.json': 
        ctyp = 'application/json'
    elif file_ext=='.zip': 
        ctyp = 'application/zip'

    extraargs = {'ContentType': ctyp}
    return extraargs


def pushToWebsite(archbucket, fuloutdir, websitebucket, orbname, s3):
    yr = orbname[:4]
    ym = orbname[:6]
    ymd = orbname[:8]

    targpth = f'reports/{yr}/orbits/{ym}/{ymd}/{orbname}/'

    objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=fuloutdir)
    if objlist['KeyCount'] > 0:
        keys = objlist['Contents']
        for k in keys:
            fname = k['Key']
            _, locfname = os.path.split(fname)
            copysrc = {'Bucket': archbucket, 'Key': fname}
            targfile = targpth + locfname
            extraargs = getExtraArgs(locfname)
            # print(targfile, extraargs)
            s3.meta.client.copy(copysrc, websitebucket, targfile, ExtraArgs=extraargs)

    while objlist['IsTruncated'] is True:
        contToken = objlist['NextContinuationToken'] 
        objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=fuloutdir, ContinuationToken=contToken)
        if objlist['KeyCount'] > 0:
            keys = objlist['Contents']
            for k in keys:
                fname = k['Key']
                _, locfname = os.path.split(fname)
                copysrc = {'Bucket': archbucket, 'Key': fname}
                targfile = targpth + locfname
                extraargs = getExtraArgs(locfname)
                # print(targfile, extraargs)
                s3.meta.client.copy(copysrc, websitebucket, targfile, ExtraArgs=extraargs)

    return 


if __name__ == '__main__':
    if len(sys.argv)>1:
        key = sys.argv[1]
    else:
        key = 'matches/RMSCorrelate/trajectories/2022/202202/20220211/20220211_233015.510_UK/20220211_233015_trajectory.pickle'

    # NB: IN THE CONSOLE, ADD TRUST RELATIONSHIP 
    # "AWS": "arn:aws:iam::317976261112:root"
    # on the target role. 

    # create an STS client object that represents a live connection to the 
    # STS service
    sts_client = boto3.client('sts')
    
    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    assumed_role_object=sts_client.assume_role(
        RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
        RoleSessionName="GetExtraFilesV2")
    
    # From the response that contains the assumed role, get the temporary 
    # credentials that can be used to make subsequent API calls
    credentials=assumed_role_object['Credentials']
    
    # Use the temporary credentials that AssumeRole returns to connections
    s3 = boto3.resource('s3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    ddb = boto3.resource('dynamodb', region_name='eu-west-1',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']) #, endpoint_url="http://thelinux:8000")

    archbucket = os.getenv('UKMONSHAREDBUCKET', default='ukmon-shared')
    websitebucket = os.getenv('WEBSITEBUCKET', default='ukmeteornetworkarchive')

    generateExtraFiles(key, archbucket, websitebucket, ddb, s3)
    

def lambda_handler(event, context):
    # NB: IN THE CONSOLE, ADD TRUST RELATIONSHIP 
    # "AWS": "arn:aws:iam::317976261112:root"
    # on the target role (replace  by this lambda's ARN). 

    # Note: if the lambda is connected to a VPC you must 
    # create a private subnet for the lambda
    # create a NAT gateway on a public subnet
    # create a routing table on the VPC to send 0.0.0.0/0 to the NAT gw
    # attach the new subnet to the NAT gw
    # 

    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()['Account']
    if response == '317976261112':
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            RoleSessionName="GetExtraFilesV2")
        
        credentials=assumed_role_object['Credentials']
        
        # Use the temporary credentials that AssumeRole returns to connections
        s3 = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
        ddb = boto3.resource('dynamodb', region_name='eu-west-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']) 
    else:
        s3 = boto3.resource('s3')
        ddb = boto3.resource('dynamodb', region_name='eu-west-1')

    websitebucket = os.getenv('WEBSITEBUCKET')
    if websitebucket[:3] == 's3:':
        websitebucket = websitebucket[5:]

    # Get the object from the event and show its content type
    archbucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        generateExtraFiles(key, archbucket, websitebucket, ddb, s3)

    except Exception as e:
        print(e)
        print(f'Error processing {key}')
        raise e
