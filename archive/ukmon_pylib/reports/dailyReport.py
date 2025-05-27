# Copyright (C) 2018-2023 Mark McIntyre
# scan the live stream for potential matches

import os
import glob
import sys
import datetime

from meteortools.utils import sendAnEmail


def AddHeader(body, bodytext, stats):
    rtstr = datetime.datetime.strptime(stats[4], '%H:%M:%S').strftime('%Hh%Mm')
    body = body + '<br>Today we examined {} detections, found {} potential matches and confirmed {} in {}.<br>'.format(stats[1], stats[2], stats[3], rtstr)
    if int(stats[3]) > 0:
        body = body + 'Up to the 100 brightest matched events are shown below. '
        body = body + 'Note that this may include older data for which a new match has been found.<br>'
        body = body + 'Click each link to see analysis of these events.<br>'
        bodytext = bodytext + 'Events: {}, Trajectories: {}. Matches {}'.format(stats[1], stats[2], stats[3])
        bodytext = bodytext + 'The following multiple detections were found in the last 24 hour period,\n'
        bodytext = bodytext + 'Note that this may include older data for which a new match has been found.\n'
        body = body + '<table border=\"0\">'
        body = body + '<tr><td><b>Event</b></td><td><b>Shwr</b></td><td><b>Vis Mag</b></td><td><b>Stations</b></td></tr>'
    else:
        body = body + '<table border=\"0\">'
    return body, bodytext


def addFooter(body, bodytext):
    fbm = 'Seen a fireball? <a href=http://fireballs.imo.net/?org=spa>Click here</a> to report it'
    body = body + '</table><br><br>\n' + fbm + '<br>'
    bodytext = bodytext + '\n' + fbm + '\n'
    return body, bodytext


def AddRowRMS(body, bodytext, ele):
    lnkpathRMS = '/reports/{:s}/orbits/{:s}/{:s}/{:s}/index.html'
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
    body = ''
    body, bodytext = AddHeader(body, bodytext, stats)

    # extract yesterday's data
    yest = datetime.date.today() - datetime.timedelta(days=doff)


    mailsubj = 'Daily matches for {:04d}-{:02d}-{:02d}'.format(yest.year, yest.month, yest.day)
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
            body, bodytext = AddRowRMS(body, bodytext, li)
        if len(lines) == 0:
            body = body + '<tr><td>There were no matches today</td></tr>'
            bodytext = bodytext + 'No matches today'
    
    body, bodytext = addFooter(body, bodytext)
    return domail, mailsubj, body, bodytext


if __name__ == '__main__':
    doff = int(sys.argv[1])
    reppth = sys.argv[2]
    outpth = sys.argv[3]
    repdtstr = (datetime.date.today() - datetime.timedelta(days=doff-1)).strftime('%Y%m%d')
    dailyreps = glob.glob(os.path.join(reppth, f'{repdtstr}*.txt'))
    dailyreps.sort()
    dailyrep = dailyreps[-1]
    statfile = os.path.join(reppth, 'stats.txt')
    _, _, body, bodytext = LookForMatchesRMS(doff, dailyrep, statfile)

    #body = body.replace('assets/img/logo.svg', 'latest/dailyreports/dailyreportsidx.html')
    if doff == 1:
        outfname = 'report_latest.html'
    else:
        yest = datetime.date.today() - datetime.timedelta(days=doff-1)
        outfname = f'{yest.strftime("report_%Y%m%d.html")}'
    with open(os.path.join(outpth, outfname), 'w') as outf:
        outf.write('<a href=/latest/dailyreports/dailyreportsidx.html>Index of daily Reports</a><br>\n')
        outf.write(body)
    
    # now send the post to groups.io
    targeturl='https://archive.ukmeteors.co.uk'

    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    recs = open(os.path.join(datadir, 'admin','dailyReportRecips.txt'), 'r').readlines()
    mailFrom = 'markmcintyre99@googlemail.com'
    mailRecip = recs[0].strip()
    if len(recs) > 1:
        mailFrom = recs[-1].strip()
    #mailRecip = 'markmcintyre99@googlemail.com' # TODO for testing only
    yest = (datetime.date.today()-datetime.timedelta(days=doff)).strftime('%Y-%m-%d')
    mailSubj = f'Latest Match Report for {yest}'
    sendAnEmail(mailRecip, bodytext, mailSubj, mailFrom, msg_html=body.replace('href="/reports', f'href="{targeturl}/reports'))
