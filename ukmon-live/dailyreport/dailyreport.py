# scan the live stream for potential matches

import os
import sys
import datetime
import boto3
from botocore.exceptions import ClientError
import numpy
import math
# import botocore
# from urllib.parse import unquote_plus
# import csv
import createIndex

idxtype = numpy.dtype([('YMD', 'i4'), ('HMS', 'i4'), ('SID', 'S16'), ('LID', 'S6'),
    ('Bri', 'f8'), ('RMS', 'f8')])
lnkpath = 'https://live.ukmeteornetwork.co.uk/M{:08d}_{:06d}_{:s}_{:s}P.jpg'


def MakeFileWritable(ymd, hms, sid, lid):
    s3 = boto3.resource('s3')
    api_client = s3.meta.client
    bucket_name = 'ukmon-live'
    key = 'M{:08d}_{:06d}_{:s}_{:s}P.jpg'.format(ymd, hms, sid, lid)
    response = api_client.copy_object(Bucket=bucket_name,
        Key=key, ContentType='image/jpeg',
        MetadataDirective='REPLACE', CopySource=bucket_name + '/' + key)


def AddHeader(body, bodytext):
    body = body + '\nThe following multiple detections were found in UKMON Live in the last 24 hour period.\n'
    body = body + '<a href=\"https://ukmeteornetwork.co.uk/live/#/\">Click here</a> to see these events.\n'
    body = body + '<table border=\"0\">'
    body = body + '<tr><td><b>Station</b></td><td><b>LID</b></td><td><b>Date/Time</b></td><td><b>Bright</b></td><td><b>RMS</b></td></tr>'
    bodytext = bodytext + 'The following multiple detections were found in UKMON Live the last 24 hour period,\n'
    return body, bodytext


def AddBlank(body, bodytext):
    body = body + '<tr><td>&nbsp;</td></tr>\n'
    bodytext = bodytext + '\n'
    return body, bodytext


def addFooter(body, bodytext):
    brim = 'Bright = max brightnes recorded by UFO '
    rmsm = 'RMS = residual error in straight line fit to the meteor path'
    pim = 'Note: Bright and RMS not available for Pi cameras'
    fbm = 'Seen a fireball? <a href=https://ukmeteornetwork.co.uk/fireball-report/>Click here</a> to report it'
    body = body + '</table><br><br>\n' + brim + '<br>' + rmsm + '<br>' + pim + '<br><br>' + fbm + '<br>'
    bodytext = bodytext + '\n' + brim + '\n' + rmsm + '\n' + '\n' + pim + '\n' + fbm + '\n'
    return body, bodytext


def AddRow(body, bodytext, ele):
    ymd, hms = ele['YMD'], ele['HMS']
    lid, sid = ele['LID'].decode('utf-8'), ele['SID'].decode('utf-8')
    if lid == 'L1':
        sid = 'Lockyer1'
    if lid == 'L2':
        sid = 'Lockyer2'
    if lid == 'NE' and sid == 'Exeter':
        sid = 'EXETER1'
    if lid == 'SW' and sid == 'Exeter':
        sid = 'Exeter2'
    bri, rms = ele['Bri'], ele['RMS']
    lnkstr = lnkpath.format(ymd, hms, sid, lid)
    hmss = '{:06d}'.format(hms)
    ymds = str(ymd)[:4] + '-' + str(ymd)[4:6] + '-' + str(ymd)[6:8] + 'T' + hmss[:2] + ':' + hmss[2:4] + ':' + hmss[4:6] + 'Z'
    str1 = '<tr><td>{:s}</td><td>{:s}</td><td><a href={:s}>{:s}</a></td><td>{:.1f}</td><td>{:.1f}</td></tr>'.format(sid, lid,
        lnkstr, ymds, bri, rms)
    str2 = '{:16s} {:6s} {:s} Bri={:.1f} RMS={:.1f}'.format(sid, lid, ymds, bri, rms)
    body = body + str1 + '\n'
    bodytext = bodytext + str2 + '\n'
    MakeFileWritable(ymd, hms, sid, lid)
    return body, bodytext


def LookForMatches(doff, idxfile, idxfile2=None):
    print('DailyCheck: looking for matches')
    bodytext = 'Daily notification of matches\n\n'
    body = '<img src=\"https://ukmeteornetwork.co.uk/img/ukmon-logo.png\" alt=\"UKMON banner\"><br>'
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
        if rw['LID'].length > 2:
            rw['HMS'] = rw['HMS'] - 2

    mailsubj = 'Daily UKMON matches for {:04d}-{:02d}-{:02d}'.format(yest.year, yest.month, yest.day)
    domail = False
    print('DailyCheck: ', mailsubj)
    # iterate looking for matches
    lasttm = 0
    # print(reldata)
    for rw in reldata:
        tm = rw['HMS']
        cond = abs(reldata['HMS'] - tm) < 5
        matchset = reldata[cond]
        # print(matchset)
        if len(matchset) > 1 and abs(lasttm - tm) > 4 and tm > 120000:
            lasttm = tm
            numpy.sort(matchset)
            if len(matchset) == 2:
                m = matchset[0]
                n = matchset[1]
                if m['SID'] != n['SID']:
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
    reldata = data[data['YMD'] == ystr]
    # iterate looking for matches
    lasttm = 0
    # print(reldata)
    for rw in reldata:
        tm = rw['HMS']
        cond = abs(reldata['HMS'] - tm) < 5
        matchset = reldata[cond]
        # print(matchset)
        if len(matchset) > 1 and abs(lasttm - tm) > 4:
            lasttm = tm
            numpy.sort(matchset)
            if len(matchset) == 2:
                m = matchset[0]
                n = matchset[1]
                if m['SID'] != n['SID']:
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

    domail, mailsubj, body, bodytext = LookForMatches(doff, idxfile, idxfile2)
    os.remove(idxfile)
    if idxfile2 is not None:
        os.remove(idxfile2)
    if domail is True:
        sendMail(mailsubj, body, bodytext)
    else:
        print('DailyCheck: no matches today')


if __name__ == '__main__':
    doff = 1
    if len(sys.argv) > 1:
        doff = int(sys.argv[1])
    a = 1
    b = 2
    lambda_handler(a, b)
