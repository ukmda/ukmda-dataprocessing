import urllib.parse
import boto3
import os
import sys
import shutil
from zipfile import ZipFile
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

# modules imported from EFS filesystem
from wmplloc.Pickling import loadPickle 
from wmplloc.Math import jd2Date
from wmplloc.pickleAnalyser import createAdditionalOutput
from wmplloc import awsAthenaGlueRetr as agr
from wmplloc.createOrbitPageIndex import createOrbitPageIndex


def findSite(stationid, ddb):
    table = ddb.Table('ukmon_camdetails')
    response = table.query(KeyConditionExpression=Key('stationid').eq(stationid))
    try:
        items = response['Items']
        if len(items) > 0:
            return items[0]['site']
        else:
            return ''
    except Exception:
        print('record not found')
    return


def generateExtraFiles(key, athena_client, archbucket, websitebucket, ddb, s3):
    fuloutdir, fname = os.path.split(key)
    _, orbname = os.path.split(fuloutdir)
    tmpdir = os.getenv('TMP')
    if tmpdir is None:
        tmpdir ='/tmp'
    outdir = os.path.join(tmpdir, orbname)
    os.makedirs(outdir, exist_ok=True)
    locfname = os.path.join(outdir, fname)

    s3.meta.client.download_file(archbucket, key, locfname)
    traj = loadPickle(outdir, fname)
    traj.save_results = True

    createAdditionalOutput(traj, outdir)

    # file to write JPGs html to, for performance benefits
    jpghtml = open(os.path.join(outdir, 'jpgs.html'), 'w')
    mp4html = open(os.path.join(outdir, 'mpgs.html'), 'w')
    # loop over observations adding jpgs to the listing file
    jpgf = open(os.path.join(outdir, 'jpgs.lst'), 'w')
    mp4f = open(os.path.join(outdir, 'mpgs.lst'), 'w')

    for obs in traj.observations:
        dtref = jd2Date(obs.jdt_ref, dt_obj=True)
        dtst = dtref.timestamp()
        id = obs.station_id
        matches = agr.read(f"SELECT dtstamp,filename FROM singlepq where id='{id}' and dtstamp > {dtst}-5 and dtstamp < {dtst}+5 ", 
            archbucket, athena_client, 'ukmonsingledata')
        if len(matches) > 0:
            edt = datetime.fromtimestamp(matches.dtstamp[0])
            ffname, _ = os.path.splitext(matches.filename[0])
            jpgname=f'img/single/{edt.year}/{edt.year}{edt.month:02d}/{ffname}.jpg'
            mp4name=f'img/mp4/{edt.year}/{edt.year}{edt.month:02d}/{ffname}.mp4'

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
            fldr = site + '/' + id
            findOtherFiles(edt, archbucket, outdir, fldr, s3)

    jpghtml.close()
    mp4html.close()
    jpgf.close()
    mp4f.close()

    repfname = locfname.replace('trajectory.pickle', 'report.txt')
    key2 = key.replace('trajectory.pickle', 'report.txt')
    s3.meta.client.download_file(archbucket, key2, repfname)

    # pushFilesBack creates the zipfile so we need to do this first
    pushFilesBack(outdir, archbucket, fuloutdir, s3)
    createOrbitPageIndex(outdir)

    idxname = os.path.join(outdir, 'index.html')
    key = os.path.join(fuloutdir, 'index.html')
    extraargs = getExtraArgs('index.html')
    s3.meta.client.upload_file(idxname, archbucket, key, ExtraArgs=extraargs) 
    
    pushToWebsite(archbucket, fuloutdir, websitebucket, orbname, s3)
    try:
        shutil.rmtree(outdir)
    except Exception:
        print(f'unable to remove {outdir}')
    return 


def findOtherFiles(evtdate, archbucket, outdir, fldr, s3):
    # if the event is after midnight the folder will have the previous days date
    if evtdate.hour < 12:
        evtdate += timedelta(days=-1)
    yr = evtdate.year
    ym = evtdate.year * 100 + evtdate.month
    ymd = ym *100 + evtdate.day

    thispth = 'archive/{:s}/{:04d}/{:06d}/{:08d}/'.format(fldr, yr, ym, ymd)
    objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=thispth)
    if objlist['KeyCount'] > 0:
        keys = objlist['Contents']
        for k in keys:
            fname = k['Key']
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
                if '.csv' in fname or '.kml' in fname or 'FTPdetectinfo' in fname:
                    _, locfname = os.path.split(fname)
                    locfname = os.path.join(outdir, locfname)
                    s3.meta.client.download_file(archbucket, fname, locfname)

    return


def pushFilesBack(outdir, archbucket, fldr, s3):
    # get filelist before creating the zipfile! 
    flist = os.listdir(outdir)

    _, pth =os.path.split(outdir)
    zipfname = os.path.join(outdir, pth +'.zip')
    zipfile = ZipFile(zipfname, 'w')

    for f in flist:
        locfname = os.path.join(outdir, f)
        zipfile.write(locfname)
        if 'pickle' not in f:
            key = os.path.join(fldr, f)
            # print(locfname, key)
            extraargs = getExtraArgs(locfname)
            s3.meta.client.upload_file(locfname, archbucket, key, ExtraArgs=extraargs) 

    zipfile.close()
    # now we push the zipfile
    key = os.path.join(fldr, pth + '.zip')
    extraargs = getExtraArgs(zipfname)
    s3.meta.client.upload_file(zipfname, archbucket, key, ExtraArgs=extraargs) 
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
        RoleSessionName="AssumeRoleSession1")
    
    # From the response that contains the assumed role, get the temporary 
    # credentials that can be used to make subsequent API calls
    credentials=assumed_role_object['Credentials']
    
    # Use the temporary credentials that AssumeRole returns to connections
    athena_client = boto3.client(service_name='athena', region_name='eu-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    s3 = boto3.resource('s3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    ddb = boto3.resource('dynamodb', region_name='eu-west-1',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']) #, endpoint_url="http://thelinux:8000")

    archbucket = os.getenv('UKMONSHAREDBUCKET')
    websitebucket = os.getenv('WEBSITEBUCKET')

    generateExtraFiles(key, athena_client, archbucket, websitebucket, ddb, s3)
    

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

    assumed_role_object=sts_client.assume_role(
        RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
        RoleSessionName="AssumeRoleSession1")
    
    credentials=assumed_role_object['Credentials']
    
    # Use the temporary credentials that AssumeRole returns to connections
    athena_client = boto3.client(service_name='athena', region_name='eu-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    s3 = boto3.resource('s3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    ddb = boto3.resource('dynamodb', region_name='eu-west-1',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']) #, endpoint_url="http://thelinux:8000")

    websitebucket = os.getenv('WEBSITEBUCKET')

    # Get the object from the event and show its content type
    archbucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        generateExtraFiles(key, athena_client, archbucket, websitebucket, ddb, s3)

    except Exception as e:
        print(e)
        print(f'Error processing {key}')
        raise e
