# Copyright (C) 2018-2023 Mark McIntyre
#
# Python script to get cameras with problems or that have not uploaded for X days
#

import os
import sys
import pandas as pd
import datetime
import textwrap

from meteortools.utils import sendAnEmail

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
