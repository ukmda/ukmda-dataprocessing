# scan the live stream for potential matches

import os
import datetime
import boto3
from botocore.exceptions import ClientError


def AddHeader(body, bodytext, stats):
    rtstr = datetime.datetime.strptime(stats[4], '%H:%M:%S').strftime('%Hh%Mm')
    body = body + '<br>Today we examined {} detections, found {} potential matches and confirmed {} in {}.<br>'.format(stats[1], stats[2], stats[3], rtstr)
    body = body + 'Up to the 100 brightest matched events are shown below. '
    body = body + 'Note that this may include older data for which a new match has been found.<br>'
    body = body + 'Click each link to see analysis of these events.<br>'
    body = body + '<table border=\"0\">'
    body = body + '<tr><td><b>Event</b></td><td><b>Shwr</b></td><td><b>Vis Mag</b></td><td><b>Stations</b></td></tr>'
    bodytext = bodytext + 'Events: {}, Trajectories: {}. Matches {}'.format(stats[1], stats[2], stats[3])
    bodytext = bodytext + 'The following multiple detections were found in UKMON Live the last 24 hour period,\n'
    bodytext = bodytext + 'Note that this may include older data for which a new match has been found.\n'
    return body, bodytext


def AddBlank(body, bodytext):
    body = body + '<tr><td>&nbsp;</td></tr>\n'
    bodytext = bodytext + '\n'
    return body, bodytext


def addFooter(body, bodytext):
    fbm = 'Seen a fireball? <a href=https://ukmeteornetwork.co.uk/fireball-report/>Click here</a> to report it'
    body = body + '</table><br><br>\n' + fbm + '<br>'
    bodytext = bodytext + '\n' + fbm + '\n'
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
    stats=''
    for s in range(4,len(spls)):
        stats = stats + spls[s] +' '

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
            body = '<tr><td>No matches today</td></tr>'
            bodytext = 'No matches today'
            # domail = True
    
    body, bodytext = addFooter(body, bodytext)
    return domail, mailsubj, body, bodytext


def sendMail(subj, body, bodytext, target, tmppth):
    print(bodytext)
    SENDER = 'ukmeteornetwork@gmail.com'
    AWS_REGION = 'eu-west-2'
    CHARSET = "UTF-8"

    s3 = boto3.resource('s3')

    deb = os.getenv('DEBUG', default='True')
    if deb.upper() == 'TRUE':
        RECIPIENT = ['mark.jm.mcintyre@cesmail.net', 'mjmm456@gmail.com']
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
            RECIPIENT = ['mark.jm.mcintyre@cesmail.net', 'mjmm456@gmail.com']

    sesclient = boto3.client('ses', region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
        response = sesclient.send_email(
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
    target = 'ukmon-shared'
    tmppth = os.getenv('TMP', default='/tmp')
    doff = os.getenv('OFFSET', default=1)

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

        domail, mailsubj, body, bodytext = LookForMatchesRMS(int(doff), dailyreport, statfile)
    except:
        domail = False

    if domail is True:
        sendMail(mailsubj, body, bodytext, target, tmppth)
    else:
        print('DailyCheck: no matches today')


if __name__ == '__main__':
    a = 1
    b = 2
    lambda_handler(a, b)
