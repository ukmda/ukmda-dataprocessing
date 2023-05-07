# Copyright (C) 2018-2023 Mark McIntyre
#
# Python script to get cameras with problems or that have not uploaded for X days
#

import os
import sys
import pandas as pd
import datetime
import boto3
import textwrap

from ukmon_meteortools.utils import sendAnEmail

mailfrom = 'ukmonhelper@ukmeteornetwork.co.uk'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python reportBadCameras.py daysback')
        exit(0)

    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    if datadir is None:
        print('define DATADIR first')
        exit(1)
    
    latemsg1 = textwrap.dedent("""
        Hi, this is to let you know that camera {} has not uploaded to UKMON for {} days.

        If you've taken the camera offline for maintenance you can ignore this message. 
        Otherwise you might want to check that the camera and Pi are working as expected and 
        the Pi has an internet connection. 

        If the camera is still offline after another 7 days you will recieve another notification.
        Regards
        The UKMON team
        """)
    latemsg2 = textwrap.dedent("""
        Hi, this is to let you know that camera {} has not uploaded to UKMON for {} days.

        If you've taken the camera offline for maintenance you can ignore this message. 
        Otherwise you might want to check that the camera and Pi are working as expected and 
        the Pi has an internet connection. 

        Regards
        The UKMON team
        """)

    badmsg = textwrap.dedent("""
        Hi, this is to let you know that camera {} attempted to upload {} events.
        Anything over 500 detections is unusual and suggests bad data.
        The questionable data was uploaded in {}.

        To check for possible causes, look at the all-night timelapse or all-night
        stack of meteors. Possible culprits are fast-moving cloud lit by moonlight, 
        moving vegetation, security lights flicking off and on, and anything that might 
        attract insects. 

        Unless you spot an interesting event on the stack or timelapse, there is no need
        to manually clean up the data. It can be really time consuming. However, if 
        you would like to do it, you use CMN_BinViewer by following the Confirmation 
        process explained at the link below. 
        https://github.com/markmac99/ukmon-pitools/wiki/Using-Binviewer
        Once you've eliminated the bad data, please send the new FTPdetect file from the 
        ConfirmedFiles folder to this email address.

        Regards
        The UKMON team
    """)

    mailmsg = ''
    camowners = pd.read_csv(os.path.join(datadir, 'admin', 'stationdetails.csv'))
    camowners = camowners.rename(columns={'camid':'stationid'})
    dts = pd.read_csv(os.path.join(datadir,'reports','camuploadtimes.csv'), index_col=False)
    dts['tcol']=[t.zfill(6) for t in dts.uploadtime.map(str)]
    dts['DateTime']=dts.upddate.map(str)+'_'+dts.tcol
    dts['ts']=[datetime.datetime.strptime(d, '%Y%m%d_%H%M%S') for d in dts.DateTime]
    dts = dts.drop(columns=['DateTime', 'tcol','manual'])
    targdate=datetime.date.today() + datetime.timedelta(days=-int(sys.argv[1]))

    subj = 'camera upload missing'
    latecams = dts[dts.ts.dt.date == targdate]
    if len(latecams) > 0:
        print('\nNot Uploaded for {} days'.format(sys.argv[1]))
        print('=========================')
        mailmsg = mailmsg + '\nNot Uploaded for {} days\n'.format(sys.argv[1])
        mailmsg = mailmsg + '=======================\n'
        latecams = pd.merge(latecams, camowners, on=['stationid'])
        latecams = latecams.drop(columns=['upddate','uploadtime'])
        print(latecams)
        
        for _, row in latecams.iterrows():
            mailrecip = row['eMail']
            statid = row['stationid']
            dayslate = int(sys.argv[1])
            #sendAnEmail(mailrecip, latemsg1.format(statid, dayslate), subj, mailfrom)
            mailmsg = mailmsg + '{} {} {}\n'.format(row['stationid'], row['ts'], row['eMail'])

    subj = 'camera upload missing - final notice'
    longerdt = int(sys.argv[1])+7
    targdate=datetime.date.today() + datetime.timedelta(days=-longerdt)

    latecams = dts[dts.ts.dt.date == targdate]
    if len(latecams) > 0:
        print('\nNot Uploaded for {} days'.format(longerdt))
        print('============================')
        mailmsg = mailmsg + '\nNot Uploaded for {} days\n'.format(longerdt)
        mailmsg = mailmsg + '============================\n'
        latecams = pd.merge(latecams, camowners, on=['stationid'])
        latecams = latecams.drop(columns=['upddate','uploadtime'])
        print(latecams)
        for _, row in latecams.iterrows():
            mailrecip = row['eMail']
            statid = row['stationid']
            dayslate = int(sys.argv[1]) + 7
            sendAnEmail(mailrecip, latemsg1.format(statid, dayslate), subj, mailfrom)
            mailmsg = mailmsg + '{} {} {}\n'.format(row['stationid'], row['ts'], row['eMail'])


    sts_client = boto3.client('sts')
    assumed_role_object=sts_client.assume_role(
        RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
        RoleSessionName="AssumeRoleSession1")
    
    # Use the temporary credentials that AssumeRole returns to connections
    credentials=assumed_role_object['Credentials']        
    logcli = boto3.client('logs', 
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'], 
        region_name='eu-west-2')

    chkdt = datetime.datetime.now() + datetime.timedelta(days=-1)
    chkdt = chkdt.replace(hour=0, minute=0, second=0, microsecond=0)
    print(chkdt)
    uxt = int(chkdt.timestamp()*1000)

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
            ftpname = spls[5]
            spls = spls[5].split('_')
            statid = spls[1]
            dat = datetime.datetime.strptime(spls[2] + '_' + spls[3], '%Y%m%d_%H%M%S')
            badcams.append([statid, dat, badcount, ftpname])
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
                ftpname = spls[5]
                spls = spls[5].split('_')
                statid = spls[1]
                dat = datetime.datetime.strptime(spls[2] + '_' + spls[3], '%Y%m%d_%H%M%S')
                badcams.append([statid, dat, badcount, ftpname])
        if 'nextToken' not in response:
            break

    subj = 'too many detections - likely bad data'
    if len(badcams) > 0: 
        print('\nToo many detections\n===================')
        mailmsg = mailmsg + '\nToo many detections\n'
        mailmsg = mailmsg + '===================\n'
        badcams = pd.DataFrame(badcams, columns=['stationid','ts','reccount','ftpname'])
        badcams = pd.merge(badcams, camowners, on=['stationid'])
        badcams = badcams.drop(columns=['site'])
        badcams = badcams[badcams.ts >= chkdt]
        print(badcams)
        for _, row in badcams.iterrows():
            mailrecip = row['eMail']
            statid = row['stationid']
            reccount = row['reccount']
            ftpname = row['ftpname']
            sendAnEmail(mailrecip, badmsg.format(statid, reccount, ftpname), subj, mailfrom)
            mailmsg = mailmsg + '{} {} {} {}\n'.format(row['stationid'], row['ts'], row['reccount'], row['eMail'])

    mailrecip = 'markmcintyre99@googlemail.com'
    msgtype='Late or Misbehaving camera report'
        
    # check again as we just applied a 2nd filter (on date)
    if len(badcams) > 0: 
        sendAnEmail(mailrecip, mailmsg, msgtype, mailfrom)
        print('mail sent')
