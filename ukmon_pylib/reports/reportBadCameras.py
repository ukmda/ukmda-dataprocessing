#
# Python script to get cameras with problems or that have not uploaded for X days
#

import os
import sys
import pandas as pd
import datetime
import boto3
import textwrap

from utils import sendAnEmail


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python reportBadCameras.py daysback')
        exit(0)

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)
    
    latemsg1 = textwrap.dedent("""
        Hi, this is to let you know that your camera {} has not uploaded to UKMON for {} days.

        If you've taken the camera offline for maintenance you can ignore this message. 
        Otherwise you might want to check that the camera and Pi are working as expected and 
        the Pi has an internet connection. 

        If the camera is still offline after another 7 days you will recieve another notification.
        Regards
        The UKMON team
        """)
    latemsg2 = textwrap.dedent("""
        Hi, this is to let you know that your camera {} has not uploaded to UKMON for {} days.

        If you've taken the camera offline for maintenance you can ignore this message. 
        Otherwise you might want to check that the camera and Pi are working as expected and 
        the Pi has an internet connection. 

        Regards
        The UKMON team
        """)

    badmsg = textwrap.dedent("""
        Hi, this is to let you know that camera {} attempted to upload {} events last night.
        Anything over 500 detections is unusual and suggests bad data.

        We suggest you check for vegetation that might have grown into the field of view, 
        security lights that might be flicking off and on, and anything that might attract
        insects into the field of view. 

        If you would like to clean up the data, you can do so using CMN_BinViewer, 
        following the Confirmation process explained at the link below. 
        https://github.com/markmac99/ukmon-pitools/wiki/Using-Binviewer
        Then please post the new FTPDetect file in groups.io/ukmeteornetwork so we can process it.

        Regards
        The UKMON team
    """)

    mailmsg = ''
    camowners = pd.read_csv(os.path.join(datadir, 'admin', 'stationdetails.csv'))
    camowners = camowners.rename(columns={'camid':'StationID'})
    dts = pd.read_csv(os.path.join(datadir,'latest','uploadtimes.csv'), index_col=False)
    dts = dts.assign(ts=pd.to_datetime(dts.DateTime))
    dts = dts.drop(columns=['DateTime'])
    targdate=datetime.date.today() + datetime.timedelta(days=-int(sys.argv[1]))

    subj = 'camera upload missing'
    latecams = dts[dts.ts.dt.date == targdate]
    if len(latecams) > 0:
        print('\nNot Uploaded for {} days'.format(sys.argv[1]))
        print('=========================')
        mailmsg = mailmsg + '\nNot Uploaded for {} days\n'.format(sys.argv[1])
        mailmsg = mailmsg + '=======================\n'
        latecams = pd.merge(latecams, camowners, on=['StationID'])
        latecams = latecams.drop(columns=['site'])
        print(latecams)
        
        for _, row in latecams.iterrows():
            mailrecip = row['eMail']
            statid = row['StationID']
            dayslate = int(sys.argv[1])
            sendAnEmail.sendAnEmail(mailrecip, latemsg1.format(statid, dayslate), subj)
            mailmsg = mailmsg + '{} {} {}\n'.format(row['StationID'], row['ts'], row['eMail'])

    subj = 'camera upload missing - final notice'
    longerdt = int(sys.argv[1])+7
    targdate=datetime.date.today() + datetime.timedelta(days=-longerdt)

    latecams = dts[dts.ts.dt.date == targdate]
    if len(latecams) > 0:
        print('\nNot Uploaded for {} days'.format(longerdt))
        print('============================')
        mailmsg = mailmsg + '\nNot Uploaded for {} days\n'.format(longerdt)
        mailmsg = mailmsg + '============================\n'
        latecams = pd.merge(latecams, camowners, on=['StationID'])
        latecams = latecams.drop(columns=['site'])
        print(latecams)
        for _, row in latecams.iterrows():
            mailrecip = row['eMail']
            statid = row['StationID']
            dayslate = int(sys.argv[1] + 7)
            sendAnEmail.sendAnEmail(mailrecip, latemsg1.format(statid, dayslate), subj)
            mailmsg = mailmsg + '{} {} {}\n'.format(row['StationID'], row['ts'], row['eMail'])

    logcli = boto3.client('logs', region_name='eu-west-2')

    uxt = datetime.datetime.now() + datetime.timedelta(days=-1)
    uxt = uxt.replace(hour=0, minute=0, second=0, microsecond=0)
    print(uxt)
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

    subj = 'too many detections - likely bad data'
    if len(badcams) > 0: 
        print('\nToo many detections\n===================')
        mailmsg = mailmsg + '\nToo many detections\n'
        mailmsg = mailmsg + '===================\n'
        badcams = pd.DataFrame(badcams, columns=['StationID','ts','reccount'])
        badcams = pd.merge(badcams, camowners, on=['StationID'])
        badcams = badcams.drop(columns=['site'])
        print(badcams)
        for _, row in badcams.iterrows():
            mailrecip = row['eMail']
            statid = row['StationID']
            reccount = row['reccount']
            sendAnEmail.sendAnEmail(mailrecip, badmsg.format(statid, reccount), subj)
            mailmsg = mailmsg + '{} {} {} {}\n'.format(row['StationID'], row['ts'], row['reccount'], row['eMail'])

    mailrecip = 'markmcintyre99@googlemail.com'
    msgtype='Late or Misbehaving camera report'
    
    if len(mailmsg) > 0:
        sendAnEmail.sendAnEmail(mailrecip, mailmsg, msgtype)
        print('mail sent')
