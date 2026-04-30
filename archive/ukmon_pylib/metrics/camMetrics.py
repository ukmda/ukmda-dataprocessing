#
# Create and access dynamodb tables containing camera upload timings etc
#
# Copyright (C) 2018-2023 Mark McIntyre

import boto3
import os
import sys
import glob
from boto3.dynamodb.conditions import Key
import pandas as pd
import datetime

from reports.CameraDetails import loadLocationDetails


def addRowCamTimings(s3bucket, s3object, ftpname, ddb=None):
    s3c = boto3.client('s3')
    dtstamp = s3c.head_object(Bucket=s3bucket, Key=s3object)['LastModified']

    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') #, endpoint_url="http://thelinux:8000")

    table = ddb.Table('uploadtimes')
    spls = ftpname.split('_')
    #print(spls[0], dtstamp)
    if spls[-1] == 'manual.txt':
        manflag = '_man'
        manual = True
    else:
        manflag = ''
        manual = False
    uploaddate = dtstamp.strftime('%Y%m%d')
    uploadtime = dtstamp.strftime('%H%M%S')
    expirydate = (dtstamp + datetime.timedelta(days=90)).timestamp()
    table.put_item(
        Item={
            'stationid': spls[1],
            'dtstamp': uploaddate + '_' + uploadtime + manflag,
            'uploaddate': int(uploaddate),
            'uploadtime': int(uploadtime),
            'manual': manual,
            'ExpiryDate': int(expirydate)
        }
    )    
    return 


# find matching entries based on stationid and upload date in yyyymmdd format
def findRowCamTimings(stationid, uploaddate, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('uploadtimes')
    response = table.query(
        KeyConditionExpression=Key('stationid').eq(stationid) & Key('dtstamp').begins_with(uploaddate)
    )
    try:
        items = response['Items']
        for item in items:
            print(item['stationid'], item['uploaddate'], item['uploadtime'],item['manual'])
    except Exception:
        print('record not found')
    return


# find matching entries based on upload date in yyyymmdd format
# aws dynamodb query --table-name uploadtimes 
# --index-name uploaddate-stationid-index 
# --key-condition-expression "uploaddate= :dt" 
# --expression-attribute-values '{":dt":{"N":"20220108"}}'

def getDayCamTimings(uploaddate, ddb=None, outfile=None, datadir=None):
    if datadir is None:
        datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('uploadtimes')
    response = table.query(
        IndexName='uploaddate-stationid-index',
        KeyConditionExpression=Key('uploaddate').eq(int(uploaddate)))

    statids = []
    updtims = []
    manuals = []
    upddts = []
    rundts = []
    try:
        items = response['Items']

        for item in items:
            statids.append(item['stationid'])
            updtims.append(item['uploadtime'])
            manuals.append(item['manual'])
            upddts.append(uploaddate)
            try:
                rundts.append(item['rundate'])
            except:
                print(f"2fudging rundate for {item['stationid']}")
                estdt = f"{uploaddate}_{int(item['uploadtime']):06d}"
                rundts.append(estdt)

        if outfile is not None:
            with open(os.path.join(datadir, 'reports', outfile), 'w') as outf:
                outf.write('stationid,upddate,uploadtime,manual\n')
                for ss,dd,tt,mm in zip(statids, upddts, updtims, manuals):
                    outf.write(f'{ss},{dd},{int(tt):06d},{mm}\n')

    except Exception:
        print('record not found')
    return statids, upddts, updtims, manuals, rundts


# read a row based on stationid and datestamp
def readRowCamTimings(stationid, dtstamp, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('uploadtimes')
    response = table.get_item(Key={'stationid': stationid,'dtstamp': dtstamp})
    try:
        item = response['Item']
        print(item['stationid'], item['uploaddate'], item['uploadtime'],item['manual'])
    except Exception:
        print('record not found')
    return


# remove a row from the table keyed on stationid adn datestamp in yyyymmdd_hhmmss format
def deleteRowCamTimings(stationid, dtstamp, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') #, endpoint_url="http://thelinux:8000")
    table = ddb.Table('uploadtimes')
    table.delete_item(Key={'stationid': stationid, 'dtstamp': dtstamp})
    return 


def backPopulate(stationid):
    s3bucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]

    basepath = os.path.expanduser('~/prod/ukmon-shared/matches/RMSCorrelate')
    fldrs = glob.glob('*', root_dir=os.path.join(basepath, stationid))
    for fldr in fldrs:
        s3objects = glob.glob('FTPd*', root_dir=os.path.join(basepath, stationid. fldr))
        if len(s3objects) > 0:
            s3obj = s3objects[0]
            fullobj = f'matches/RMSCorrelate/{stationid}/{fldr}/{s3obj}'
            print(fullobj, s3obj)
            addRowCamTimings(s3bucket, fullobj, s3obj)


if __name__ == '__main__':
    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))

    ddb = boto3.resource('dynamodb', region_name='eu-west-2') 

    s,d,t,m,r = getDayCamTimings(sys.argv[1], ddb=ddb)
    newdata=pd.DataFrame(zip(s,d,t,m,r), columns=['stationid','upddate','uploadtime','manual','rundate'])

    outfile=os.path.join(datadir, 'reports', 'camuploadtimes.csv')
    if os.path.isfile(outfile):
        currdata = pd.read_csv(outfile)
        fulldf = pd.concat([currdata, newdata], ignore_index=True)
        fulldf = fulldf.sort_values(by=['stationid','upddate','uploadtime','rundate'])
        fulldf = fulldf.drop_duplicates(subset=['stationid'], keep='last')
    else:
        fulldf = newdata
    fulldf.to_csv(outfile, index=False)

    camlist = loadLocationDetails(ddb=ddb)
    camlist=camlist[camlist.active==1]
    sep = ['_'] * len(camlist)
    pd.options.mode.chained_assignment = None  # default='warn'
    camlist['location'] = (camlist.site + sep + camlist.direction).str.lower()    
    pd.options.mode.chained_assignment = 'warn'
    caminfo = camlist.drop(columns=['site','direction','oldcode','active','camtype','eMail', 'humanName'])

    # process the last-login data from the SSHD log
    lastlogs = open(os.path.join(datadir, 'reports', 'lastlogins.txt'),'r').readlines()
    lodata = []
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    for li in lastlogs:
        spls = li.split('ssh')
        # could be ubuntu (auth.log) or amazon linux style log
        dtstr = spls[0][spls[0].find(':')+1:][:19]
        if ' ' in dtstr:
            dtval = datetime.datetime.strptime(f'{now.year} {dtstr[:15]}', '%Y %b %d %H:%M:%S')
            if dtval > now:
                dtval = dtval.replace(year=now.year-1, tzinfo=datetime.timezone.utc)
        else:
            dtval = datetime.datetime.strptime(dtstr, '%Y-%m-%dT%H:%M:%S')
            dtval = dtval.replace(tzinfo=datetime.timezone.utc)
        location = spls[1].split(' for ')[1].split()[0]
        lodata.append({'location':location, 'lastseen':dtval})


    if len(lodata) > 0:
        logindf = pd.DataFrame(lodata)
        logindf = logindf.sort_values(by=['lastseen'])
        logindf.drop_duplicates(subset=['location'], inplace=True, keep='last')

        # create a merged dataframe with siteid and stationid
        intdf = pd.merge(logindf,caminfo, on=['location'], how='outer')

        df = pd.merge(intdf, fulldf, on=['stationid'])
        df['uploadtime']=df.uploadtime.astype("str").str.pad(6,fillchar="0")
        df['lastupload']=df.upddate.astype('str') + '_' +df.uploadtime
        df.lastupload = [datetime.datetime.strptime(x, '%Y%m%d_%H%M%S') for x in df.lastupload]
        df = df.drop(columns=['stationid','manual','rundate', 'upddate','uploadtime'])
        df['dateval']=[x.strftime('%b-%d') for x in df.lastupload]
        df = df.sort_values(by=['lastupload'])

        outfile=os.path.join(datadir, 'reports', 'stationlogins.txt')
        zerodate = datetime.datetime(1970,1,1,0,0,0)
        with open(outfile,'w') as outf:
            outf.write('Last Upload,      StationID,         Last Login\n')
            for _,rw in df.iterrows():
                dtval = rw.dateval
                lastup = rw.lastupload.strftime('%H:%M:%S')
                if pd.isnull(rw.lastseen):
                    lastseen = '> 1 month'
                else:
                    lastseen = rw.lastseen.strftime('%b-%d %H:%M:%S')
                if lastseen == 'Jan-01 00:00:00':
                    lastseen = '> 1 month'
                outf.write(f'{dtval}, {lastup}, {rw.location:20s}, {lastseen}\n')
