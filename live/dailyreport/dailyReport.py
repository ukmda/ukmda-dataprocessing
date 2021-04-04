# scan the live stream for potential matches

import os
import sys
import datetime
import boto3
from botocore.exceptions import ClientError
import numpy
import math
import createIndex


#idxtype = numpy.dtype([('YMD', 'i4'), ('HMS', 'i4'), ('SID', 'S16'), ('LID', 'S6'),
#    ('Bri', 'i4')])
lnkpath = 'https://live.ukmeteornetwork.co.uk/M{:08d}_{:06d}_{:s}_{:s}P.jpg'
lnkpathRMS = 'https://archive.ukmeteornetwork.co.uk/reports/{:s}/orbits/{:s}/{:s}/index.html'


def MakeFileWritable(ymd, hms, sid, lid):
    s3 = boto3.resource('s3')
    api_client = s3.meta.client
    bucket_name = 'ukmon-live'
    key = 'M{:08d}_{:06d}_{:s}_{:s}P.jpg'.format(ymd, hms, sid, lid)
    api_client.copy_object(Bucket=bucket_name,
        Key=key, ContentType='image/jpeg',
        MetadataDirective='REPLACE', CopySource=bucket_name + '/' + key)


def AddHeader(body, bodytext):
    body = body + '\nThe following matched detections were found in the last 24 hour period.\n'
    body = body + 'Note that this may include older data for which a new match has been found.\n'
    body = body + 'Click each link to see analysis of these events.\n'
    body = body + '<table border=\"0\">'
    body = body + '<tr><td><b>Event</b></td><td><b>Stations</b></td></tr>'
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


def AddRow(body, bodytext, ele):
    ymd, hms = ele['YMD'], ele['HMS']
    lid, sid = ele['LID'].decode('utf-8'), ele['SID'].decode('utf-8')
    bri = ele['Bri']
    lnkstr = lnkpath.format(ymd, hms, sid, lid)
    hmss = '{:06d}'.format(hms)
    ymds = str(ymd)[:4] + '-' + str(ymd)[4:6] + '-' + str(ymd)[6:8] + 'T' + hmss[:2] + ':' + hmss[2:4] + ':' + hmss[4:6] + 'Z'
    str1 = '<tr><td>{:s}</td><td>{:s}</td><td><a href={:s}>{:s}</a></td><td>{:.1f}</td></tr>'.format(sid, lid,
        lnkstr, ymds, bri)
    str2 = '{:16s} {:6s} {:s} Bri={:.1f}'.format(sid, lid, ymds, bri)
    body = body + str1 + '\n'
    bodytext = bodytext + str2 + '\n'
    MakeFileWritable(ymd, hms, sid, lid)
    return body, bodytext


def AddRowRMS(body, bodytext, ele):
    spls = ele.split(',')
    pth = spls[1]
    yr = pth[:4]
    ym = pth[:6]
    lnkstr = lnkpathRMS.format(yr, ym, pth)
    stats='Match between '
    for s in range(2,len(spls)):
        stats = stats + spls[s] +' '

    str1 = '<tr><td><a href="{:s}">{:s}</a></td><td>{:s}</td></tr>'.format(lnkstr, pth, stats)
    body = body + str1
    bodytext = bodytext + str1 + '\n'

    return body, bodytext


def LookForMatches(doff, idxfile, idxfile2=None):
    print('DailyCheck: looking for matches')
    bodytext = 'Daily notification of matches\n\n'
    body = '<img src=\"https://ukmeteornetwork.co.uk/assets/img/logo.svg\" alt=\"UKMON banner\"><br>'
    body, bodytext = AddHeader(body, bodytext)

    print('DailyCheck: opening csv file ', idxfile)
    csvfile = open(idxfile)
    data = numpy.loadtxt(csvfile, delimiter=',', dtype=idxtype)

    # extract yesterday's data
    yest = datetime.date.today() - datetime.timedelta(days=doff)
    ystr = (yest.year * 10000) + (yest.month * 100) + yest.day
    reldata = data[data['YMD'] == ystr]

    # correct RMS timestamps which are 2.4 seconds ahead
    for rw in reldata:
        lid = rw['LID']
        if lid[:3] == 'UK0':
            rw['HMS'] = rw['HMS'] - 2

    mailsubj = 'Daily UKMON matches for {:04d}-{:02d}-{:02d}'.format(yest.year, yest.month, yest.day)
    domail = False
    print('DailyCheck: ', mailsubj)

    # iterate looking for matches
    print('checking for ', ystr)
    lasttm = 0
    for rw in reldata:
        tm = rw['HMS']
        cond = abs(reldata['HMS'] - tm) < 5
        matchset = reldata[cond]
        if len(matchset) > 1 and abs(lasttm - tm) > 4.9999 and tm > 120000:
            lasttm = tm
            numpy.sort(matchset)
            print(len(matchset), ' matches')
            if len(matchset) == 2:
                m = matchset[0]
                n = matchset[1]
                sid1 = m['SID'].decode('utf-8')
                sid2 = n['SID'].decode('utf-8')
                if sid1 == 'EXETER1' or sid1 == 'Exeter2':
                    sid1 = 'Exeter'
                if sid2 == 'EXETER1' or sid2 == 'Exeter2':
                    sid2 = 'Exeter'
                if sid1 == 'Lockyer1':
                    sid1 = 'Lockyer'
                if sid2 == 'Lockyer2':
                    sid2 = 'Lockyer'

                if sid1 != sid2:
                    domail = True
                    body, bodytext = AddBlank(body, bodytext)
                    body, bodytext = AddRow(body, bodytext, matchset[0])
                    body, bodytext = AddRow(body, bodytext, matchset[1])
            else:
                domail = True
                body, bodytext = AddBlank(body, bodytext)
                for el in matchset:
                    body, bodytext = AddRow(body, bodytext, el)
    csvfile.close()
    if idxfile2 is None:
        idxfile2 = idxfile
    csvfile = open(idxfile2)
    data = numpy.loadtxt(csvfile, delimiter=',', dtype=idxtype)

    # extract yesterday's data
    yest = datetime.date.today() - datetime.timedelta(days=doff - 1)
    ystr = (yest.year * 10000) + (yest.month * 100) + yest.day
    reldata2 = data[data['YMD'] == ystr]
    print('now checking for ', ystr)

    # iterate looking for matches
    lasttm = 0
    # print(reldata)
    for rw in reldata2:
        tm = rw['HMS']
        cond = abs(reldata2['HMS'] - tm) < 5
        matchset = reldata2[cond]
        # print(matchset)
        if len(matchset) > 1 and abs(lasttm - tm) > 4.9999 and tm < 120000:
            lasttm = tm
            numpy.sort(matchset)
            print(len(matchset), ' matches')
            if len(matchset) == 2:
                m = matchset[0]
                n = matchset[1]
                sid1 = m['SID'].decode('utf-8')
                sid2 = n['SID'].decode('utf-8')
                if sid1 == 'EXETER1' or sid1 == 'Exeter2':
                    sid1 = 'Exeter'
                if sid2 == 'EXETER1' or sid2 == 'Exeter2':
                    sid2 = 'Exeter'
                if sid1 == 'Lockyer1':
                    sid1 = 'Lockyer'
                if sid2 == 'Lockyer2':
                    sid2 = 'Lockyer'

                if sid1 != sid2:
                    domail = True
                    body, bodytext = AddBlank(body, bodytext)
                    body, bodytext = AddRow(body, bodytext, matchset[0])
                    body, bodytext = AddRow(body, bodytext, matchset[1])
            else:
                domail = True
                body, bodytext = AddBlank(body, bodytext)
                for el in matchset:
                    print(el)
                    body, bodytext = AddRow(body, bodytext, el)
    csvfile.close()
    body, bodytext = addFooter(body, bodytext)
    return domail, mailsubj, body, bodytext


def LookForMatchesRMS(doff, dayfile):
    print('DailyCheck: looking for matches')
    bodytext = 'Daily notification of matches\n\n'
    body = '<img src=\"https://ukmeteornetwork.co.uk/assets/img/logo.svg\" alt=\"UKMON banner\"><br>'
    body, bodytext = AddHeader(body, bodytext)

    # extract yesterday's data
    yest = datetime.date.today() - datetime.timedelta(days=doff)


    mailsubj = 'Daily UKMON matches for {:04d}-{:02d}-{:02d}'.format(yest.year, yest.month, yest.day)
    domail = False
    print('DailyCheck: ', mailsubj)

    print('DailyCheck: opening csv file ', dayfile)
    with open(dayfile, 'r') as csvfile:
        lines = csvfile.readlines()
        for li in lines:
            domail = True
            #body, bodytext = AddBlank(body, bodytext)
            body, bodytext = AddRowRMS(body, bodytext, li)
    
    body, bodytext = addFooter(body, bodytext)
    return domail, mailsubj, body, bodytext


def sendMail(subj, body, bodytext):
    print(bodytext)
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        SENDER = 'mark.jm.mcintyre@cesmail.net'
        AWS_REGION = 'eu-west-2'
    else:
        SENDER = 'ukmeteornetwork@gmail.com'
        AWS_REGION = 'eu-west-1'
    CHARSET = "UTF-8"

    deb = os.environ['DEBUG']
    if deb in ['True', 'TRUE', 'true']:
        RECIPIENT = ['mark.jm.mcintyre@cesmail.net', 'mjmm456@gmail.com']
    else:
        try:
            recs = os.environ['RECIPS']
            RECIPIENT = recs.split(';')
            print('DailyCheck: ', RECIPIENT)
        except:
            RECIPIENT = ['mark.jm.mcintyre@cesmail.net', 'mjmm456@gmail.com']

    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENT,
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
        target = 'ukmon-live'
    try:
        doff = int(os.environ['OFFSET'])
    except:
        doff = 1
    # update index for requested date and today
    print('DailyCheck: updating indexes')
    createIndex.createIndex(doff)
    createIndex.createIndex(doff - 1)

    print('DailyCheck: getting indexes')
    s3 = boto3.resource('s3')
    try:
        tmppth = os.environ['TMP']
    except:
        tmppth = '/tmp'
    tod = datetime.datetime.today() - datetime.timedelta(days=doff)
    tmpf = 'idx{:04d}{:02d}.csv'.format(tod.year, math.ceil(tod.month / 3))
    idxfile = os.path.join(tmppth, tmpf)
    s3.meta.client.download_file(target, tmpf, idxfile)

    tod = datetime.datetime.today() - datetime.timedelta(days=doff - 1)
    tmpf2 = 'idx{:04d}{:02d}.csv'.format(tod.year, math.ceil(tod.month / 3))
    if tmpf2 != tmpf:
        idxfile2 = os.path.join(tmppth, tmpf2)
        s3.meta.client.download_file(target, tmpf2, idxfile2)
    else:
        idxfile2 = None
    fullrep = 'matches/RMSCorrelate/dailyreports/'+ datetime.datetime.today().strftime('%Y%m%d.txt')
    dailyreport = os.path.join(tmppth,'dailyreport.csv')
    print(target, fullrep, dailyreport)
    s3.meta.client.download_file('ukmon-shared', fullrep, dailyreport)

    domail, mailsubj, body, bodytext = LookForMatchesRMS(doff,dailyreport)

    #domail, mailsubj, body, bodytext = LookForMatches(doff, idxfile, idxfile2)
    os.remove(idxfile)
    if idxfile2 is not None:
        os.remove(idxfile2)
    if domail is True:
        sendMail(mailsubj, body, bodytext)
    else:
        print('DailyCheck: no matches today')

    print('DailyCheck: purging older data')
    createIndex.purgeOlderFiles()


if __name__ == '__main__':
    doff = 1
    if len(sys.argv) > 1:
        doff = int(sys.argv[1])
    a = 1
    b = 2
    lambda_handler(a, b)
