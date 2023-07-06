# Copyright (C) 2018-2023 Mark McIntyre
# scan the live stream for potential matches

import os
import sys
import datetime
import boto3
from botocore.exceptions import ClientError


def MakeFileWritable(ymd, hms, sid, lid):
    s3 = boto3.resource('s3')
    api_client = s3.meta.client
    bucket_name = 'ukmon-live'
    key = 'M{:08d}_{:06d}_{:s}_{:s}P.jpg'.format(ymd, hms, sid, lid)
    api_client.copy_object(Bucket=bucket_name,
        Key=key, ContentType='image/jpeg',
        MetadataDirective='REPLACE', CopySource=bucket_name + '/' + key)


def AddHeader(body, bodytext, stats):
    rtstr = datetime.datetime.strptime(stats[4], '%H:%M:%S').strftime('%Hh%Mm')
    body = body + '<br>Today we examined {} detections, found {} potential matches and confirmed {} in {}.<br>'.format(stats[1], stats[2], stats[3], rtstr)
    if int(stats[3]) > 0:
        body = body + 'Up to the 100 brightest matched events are shown below. '
        body = body + 'Note that this may include older data for which a new match has been found.<br>'
        body = body + 'Click each link to see analysis of these events.<br>'
        bodytext = bodytext + 'Events: {}, Trajectories: {}. Matches {}'.format(stats[1], stats[2], stats[3])
        bodytext = bodytext + 'The following multiple detections were found in UKMON Live the last 24 hour period,\n'
        bodytext = bodytext + 'Note that this may include older data for which a new match has been found.\n'
        body = body + '<table border=\"0\">'
        body = body + '<tr><td><b>Event</b></td><td><b>Shwr</b></td><td><b>Vis Mag</b></td><td><b>Stations</b></td></tr>'
    else:
        body = body + '<table border=\"0\">'
    return body, bodytext


def AddBlank(body, bodytext):
    body = body + '<tr><td>&nbsp;</td></tr>\n'
    bodytext = bodytext + '\n'
    return body, bodytext


def addFooter(body, bodytext):
    fbm = 'Seen a fireball? <a href=https://ukmeteornetwork.co.uk/fireball-report/>Click here</a> to report it'
    uss = 'Unsubscribe from UKMON report'
    usb = 'Please unsubscribe me from the UKMON daily report'
    usm = f'To unsubscribe <a href=\"mailto:markmcintyre99@googlemail.com?Subject={uss}&body={usb}\">click here</a>.'
    body = body + '</table><br><br>\n' + fbm + '<br>' +usm + '<br>'
    bodytext = bodytext + '\n' + fbm + '\n' + usm + '\n'
    return body, bodytext


def AddRowRMS(body, bodytext, ele):
    lnkpathRMS = 'https://archive.ukmeteornetwork.co.uk/reports/{:s}/orbits/{:s}/{:s}/{:s}/index.html'
    spls = ele.split(',')
    _, pth = os.path.split(spls[1])
    yr = pth[:4]
    ym = pth[:6]
    ymd = pth[:8]
    lnkstr = lnkpathRMS.format(yr, ym, ymd, pth)
    shwr = spls[2]
    mag = spls[3]
    if len(spls) > 4:
        stats=spls[4].replace(';', ' ')
    else:
        stats='unknown'

    str1 = '<tr><td><a href="{:s}">{:s}</a></td><td>{:s}</td><td>{:s}</td><td>{:s}</td></tr>'.format(lnkstr, pth, shwr, mag, stats)
    body = body + str1
    bodytext = bodytext + str1 + '\n'

    return body, bodytext


def LookForMatchesRMS(doff, dayfile, statsfile):
    # get stats
    with open(statsfile, 'r') as inf:
        lis = inf.readlines()
    stats = lis[-1].strip().split(' ')

    bodytext = 'Daily notification of matches\n\n'
    body = '<img src=\"https://ukmeteornetwork.co.uk/assets/img/logo.svg\" alt=\"UKMON banner\"><br>'
    body, bodytext = AddHeader(body, bodytext, stats)

    # extract yesterday's data
    yest = datetime.date.today() - datetime.timedelta(days=doff)


    mailsubj = 'Daily UKMON matches for {:04d}-{:02d}-{:02d}'.format(yest.year, yest.month, yest.day)
    domail = True
    print('DailyCheck: ', mailsubj)

    print('DailyCheck: opening csv file ', dayfile)
    with open(dayfile, 'r') as csvfile:
        try: # top 100 matches
            lines = [next(csvfile) for x in range(100)]
        except: # less than 100 so display them all
            csvfile.seek(0)
            lines = csvfile.readlines()

        for li in lines:
            # domail = True
            #body, bodytext = AddBlank(body, bodytext)
            body, bodytext = AddRowRMS(body, bodytext, li)
        if len(lines) == 0:
            body = body + '<tr><td>There were no matches today</td></tr>'
            bodytext = bodytext + 'No matches today'
            # domail = True
    
    body, bodytext = addFooter(body, bodytext)
    return domail, mailsubj, body, bodytext


def sendMail(subj, body, bodytext, target, tmppth):
    print(bodytext)
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        SENDER = 'ukmeteornetwork@gmail.com'
        AWS_REGION = 'eu-west-2'
    else:
        SENDER = 'ukmeteornetwork@gmail.com'
        AWS_REGION = 'eu-west-1'
    CHARSET = "UTF-8"

    s3 = boto3.resource('s3')

    deb = os.environ['DEBUG']
    if deb in ['True', 'TRUE', 'true']:
        RECIPIENT = ['markmcintyre99@googlemail.com', 'mjmm456@gmail.com']
    else:
        try:
            memblist = os.path.join(tmppth,'dailyReportRecips.txt')
            s3.meta.client.download_file(target, 'admin/dailyReportRecips.txt', memblist)
            with open(memblist, 'r') as inf:
                recs = inf.readlines()
                for i in range(len(recs)):
                    recs[i] = recs[i].strip()
            RECIPIENT = recs
            print('DailyCheck: ', RECIPIENT)
        except:
            RECIPIENT = ['markmcintyre99@googlemail.com', 'mjmm456@gmail.com']

    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'BccAddresses': RECIPIENT,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': bodytext,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subj,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("DailyCheck: Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):
    # check which account we're in
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        target = 'mjmm-live'
    else:
        target = 'ukmon-shared'
    try:
        doff = int(os.environ['OFFSET']) 
    except:
        doff = 1

    tmppth = '/tmp'
    print('DailyCheck: getting daily report')
    s3 = boto3.resource('s3')
    fullrep = 'matches/RMSCorrelate/dailyreports/latest.txt'
    dailyreport = os.path.join(tmppth,'dailyreport.csv')
    print(target, fullrep, dailyreport)
    try:
        s3.meta.client.download_file(target, fullrep, dailyreport)
        
        statfile = 'stats.txt'
        fullstat ='matches/RMSCorrelate/dailyreports/' + statfile
        statfile = os.path.join(tmppth, statfile)
        print(statfile, fullstat)
        s3.meta.client.download_file(target, fullstat, statfile)

        domail, mailsubj, body, bodytext = LookForMatchesRMS(doff, dailyreport, statfile)
    except:
        domail = False

    if domail is True:
        sendMail(mailsubj, body, bodytext, target, tmppth)
    else:
        print('DailyCheck: no matches today')


if __name__ == '__main__':
    doff = 1
    if len(sys.argv) == 1:
        doff = int(sys.argv[1])
        a = 1
        b = 2
        lambda_handler(a, b)
    if len(sys.argv) > 1:
        doff = int(sys.argv[1])
        reppth = sys.argv[2]
        outpth = sys.argv[3]
        repdtstr = (datetime.date.today() - datetime.timedelta(days=doff-1)).strftime('%Y%m%d.txt')
        dailyrep = os.path.join(reppth, repdtstr)
        statfile = os.path.join(reppth, 'stats.txt')
        _, _, body, _ = LookForMatchesRMS(doff, dailyrep, statfile)

        #body = body.replace('assets/img/logo.svg', 'latest/dailyreports/dailyreportsidx.html')
        if doff == 1:
            outfname = 'report_latest.html'
        else:
            yest = datetime.date.today() - datetime.timedelta(days=doff-1)
            outfname = f'{yest.strftime("report_%Y%m%d.html")}'
        with open(os.path.join(outpth, outfname), 'w') as outf:
            outf.write('<a href=/latest/dailyreports/dailyreportsidx.html>Index of daily Reports</a><br>\n')
            outf.write(body)
