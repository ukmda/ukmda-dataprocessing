# Copyright (C) 2018-2023 Mark McIntyre
# scan the live stream for potential matches

import os
import datetime
import boto3
from botocore.exceptions import ClientError


def AddHeader(body, bodytext, stats, repdate):
    rtstr = datetime.datetime.strptime(stats[4], '%H:%M:%S').strftime('%Hh%Mm')
    body = body + f'<br>On {repdate} we examined {stats[1]} detections, found {stats[2]} potential matches and confirmed {stats[3]} in {rtstr}.<br>'
    if int(stats[3]) > 0:
        body = body + 'Up to the 100 brightest matched events are shown below. '
        body = body + 'Note that this may include older data for which a new match has been found.<br>'
        body = body + 'Click each link to see analysis of these events.<br>'
        bodytext = bodytext + f'Events: {stats[1]}, Trajectories: {stats[2]}. Matches {stats[3]}\n'
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
    addlmsg = '<br>Note that we can\'t unsubscribe you if you\'re receiving the report via groups.io'
    usm = f'To unsubscribe <a href=\"mailto:markmcintyre99@googlemail.com?Subject={uss}&body={usb}\">click here</a>.{addlmsg}'
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

    tod = (datetime.date.today()).strftime('%Y-%m-%d')
    yest = (datetime.date.today()-datetime.timedelta(days=doff)).strftime('%Y-%m-%d')

    bodytext = f'Daily notification of matches on {tod}\n\n'
    body = '<img src=\"https://ukmeteornetwork.co.uk/assets/img/logo.svg\" alt=\"UKMON banner\"><br>'
    body, bodytext = AddHeader(body, bodytext, stats, tod)

    mailsubj = f'Latest UKMON Match Report for {yest}'
    domail = True
    print('DailyCheck: ', mailsubj)

    #print('DailyCheck: opening csv file ', dayfile)
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
    SENDER = 'ukmeteornetwork@gmail.com'
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        AWS_REGION = 'eu-west-2'
    else:
        AWS_REGION = 'eu-west-1'
    CHARSET = "UTF-8"

    s3 = boto3.resource('s3')

    deb = os.getenv('DEBUG', default='FALSE').upper()
    if deb == 'TRUE':
        RECIPIENT = ['markmcintyre99@googlemail.com', 'mjmm456@gmail.com']
    else:
        try:
            memblist = os.path.join(tmppth,'dailyReportRecips.txt')
            s3.meta.client.download_file(target, 'admin/dailyReportRecips.txt', memblist)
            recs = open(memblist, 'r').readlines()
            recs = list(map(lambda x: x.strip(), recs)) 
            recs = [x for x in recs if x[0] != '#'] 
            RECIPIENT = recs
            print('DailyCheck: ', RECIPIENT)
        except:
            print('unable to retrieve recipient list')
            RECIPIENT = ['markmcintyre99@googlemail.com', 'mjmm456@gmail.com']
            print('DailyCheck: ', RECIPIENT)

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
    srcbucket = os.getenv('SRCBUCKET', default='ukmda-shared')
    doff = int(os.getenv('OFFSET', default='1'))

    tmppth = '/tmp'
    print('DailyCheck: getting daily report')
    s3 = boto3.resource('s3')
    fullrep = os.getenv('DAILYFILE', default='matches/RMSCorrelate/dailyreports/latest.txt')
    dailyreport = os.path.join(tmppth,'dailyreport.csv')
    print(srcbucket, fullrep, dailyreport)
    try:
        s3.meta.client.download_file(srcbucket, fullrep, dailyreport)
        statfile = 'stats.txt'
        pth, _ = os.path.split(fullrep)
        fullstat =os.path.join(pth, statfile)
        statfile = os.path.join(tmppth, statfile)
        print(statfile, fullstat)
        s3.meta.client.download_file(srcbucket, fullstat, statfile)

        domail, mailsubj, body, bodytext = LookForMatchesRMS(doff, dailyreport, statfile)
    except:
        domail = False

    if domail is True:
        sendMail(mailsubj, body, bodytext, srcbucket, tmppth)
    else:
        print('DailyCheck: no matches today')
