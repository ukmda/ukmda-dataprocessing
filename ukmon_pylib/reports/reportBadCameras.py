#
# Python script to get cameras with problems or that have not uploaded for X days
#

import os
import sys
import pandas as pd
import datetime
import boto3


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python reportBadCameras.py daysback')
        exit(0)

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)
    
    camowners = pd.read_csv(os.path.join(datadir, 'admin', 'stationdetails.csv'))
    camowners = camowners.rename(columns={'camid':'StationID'})
    dts = pd.read_csv(os.path.join(datadir,'latest','uploadtimes.csv'), index_col=False)
    dts = dts.assign(ts=pd.to_datetime(dts.DateTime))
    dts = dts.drop(columns=['DateTime'])
    targdate=datetime.date.today() + datetime.timedelta(days=-int(sys.argv[1]))

    latecams = dts[dts.ts.dt.date == targdate]
    if len(latecams) > 0:
        print('Not Uploaded for {} days'.format(sys.argv[1]))
        print('=======================')
        latecams = pd.merge(latecams, camowners, on=['StationID'])
        latecams = latecams.drop(columns=['site'])
        print(latecams)

    longerdt = int(sys.argv[1])+7
    targdate=datetime.date.today() + datetime.timedelta(days=-longerdt)

    latecams = dts[dts.ts.dt.date < targdate]
    if len(latecams) > 0:
        print('Not Uploaded for more than {} days'.format(longerdt))
        print('==================================')
        latecams = pd.merge(latecams, camowners, on=['StationID'])
        latecams = latecams.drop(columns=['site'])
        print(latecams)

    logcli = boto3.client('logs', region_name='eu-west-2')

    uxt = datetime.datetime.now() + datetime.timedelta(days=-2)
    uxt = uxt.replace(hour=0, minute=0, second=0, microsecond=0)
    uxt = int(uxt.timestamp()*1000)

    badcams=[]
    response = logcli.filter_log_events(
        logGroupName="/aws/lambda/consolidateFTPdetect",
        startTime=uxt,
        filterPattern="too many",
        limit=1000)
    if len(response['events']) > 0:
        for i in range(len(response['events'])):
            msg = response['events'][i]['message'].strip()
            spls = msg.split(' ')
            badcount = spls[3]
            spls = spls[5].split('_')
            statid = spls[1]
            dat = datetime.datetime.strptime(spls[2] + '_' + spls[3], '%Y%m%d_%H%M%S')
            badcams.append([statid, dat, badcount])
    while True:
        currentToken = response['nextToken']
        response = logcli.filter_log_events(
            logGroupName="/aws/lambda/consolidateFTPdetect",
            startTime=uxt,
            filterPattern="too many",
            nextToken = currentToken,
            limit=1000)
        if len(response['events']) > 0:
            for i in range(len(response['events'])):
                msg = response['events'][i]['message'].strip()
                spls = msg.split(' ')
                badcount = spls[3]
                spls = spls[5].split('_')
                statid = spls[1]
                dat = datetime.datetime.strptime(spls[2] + '_' + spls[3], '%Y%m%d_%H%M%S')
                badcams.append([statid, dat, badcount])
        if 'nextToken' not in response:
            break
    if len(badcams) > 0: 
        print('')
        print('Too many detections')
        print('===================')
        badcams = pd.DataFrame(badcams, columns=['StationID','ts','reccount'])
        badcams = pd.merge(badcams, camowners, on=['StationID'])
        badcams = badcams.drop(columns=['site'])
        print(badcams)
