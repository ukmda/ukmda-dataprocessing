# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import os
import sys
import csv
import json
import pandas as pd


def createDetectionsFile(eDate, datadir, daysback=7):
    yr = datetime.datetime.now().year
    cols = ['Dtstamp','ID','Y']
    df = pd.read_parquet(os.path.join(datadir, 'single',f'singles-{yr}.parquet.snap'), columns=cols)
    df = df[df['Y']==int(yr)]
    
    sDate = eDate + datetime.timedelta(days = -daysback)
    df = df[df.Dtstamp >= sDate.timestamp()]
    df = df[df.Dtstamp <= eDate.timestamp()]
    outdf = pd.concat([df.ID, df.Dtstamp],keys=['camera_id','Dtstamp'], axis=1)
    outdf = outdf.assign(ts = pd.to_datetime(outdf['Dtstamp'], unit='s'))
    outdf['datetime'] = [ts.strftime('%Y-%m-%dT%H:%M:%S.%f') for ts in outdf.ts]
    outdf = outdf.assign(image_URL='')
    outdf.sort_values(by=['Dtstamp'], inplace=True, ascending=False)
    outdfnots = outdf.drop(columns=['Dtstamp', 'ts'])
    outdfnots = outdfnots.drop_duplicates()

    os.makedirs(os.path.join(datadir, 'browse','daily'), exist_ok=True)
    outfname = os.path.join(datadir, 'browse/daily/ukmon-latest.csv')
    outdfnots.to_csv(outfname, index=False)

    sDate = eDate + datetime.timedelta(days = -3)
    createEventList(datadir, outdf, sDate)
    return 


def createEventList(datadir, data, start_date):
    os.makedirs(os.path.join(datadir, 'browse','daily'), exist_ok=True)
    idxfile = os.path.join(datadir, 'browse/daily/eventlist.js')
    with open(idxfile, 'w') as outf:
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = "h4";\n')

        if data is not None: 
            for _, li in data.iterrows():
                if li['ts'] < start_date:
                    break
                outf.write('var row = table.insertRow(-1);\n')
                outf.write('var cell = row.insertCell(0);\n')
                outf.write('cell.innerHTML = "{}";\n'.format(li['camera_id']))
                outf.write('var cell = row.insertCell(1);\n')
                outf.write('cell.innerHTML = "{}";\n'.format(li['ts'].strftime('%Y-%m-%dT%H:%M:%S.%f')))

        outf.write('var row = header.insertRow(0);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "Camera";\n')
        outf.write('cell.className = "small";\n')
        outf.write('var cell = row.insertCell(1);\n')
        outf.write('cell.innerHTML = "Datetime";\n')
        outf.write('cell.className = "small";\n')

        outf.write('var outer_div = document.getElementById("eventlist");\n')
        outf.write('outer_div.appendChild(table);\n')

        outf.write('})\n')

    return


def createMatchesFile(sDate, datadir):
    # read and process the daily matches file
    matchf = os.path.join(datadir, 'dailyreports/{}.txt'.format(sDate.strftime('%Y%m%d')))
    with open(matchf, 'r') as inf:
        data = csv.reader(inf, delimiter=',')

        os.makedirs(os.path.join(datadir, 'browse','daily'), exist_ok=True)
        outfname = os.path.join(datadir, 'browse/daily/matchlist.js')
        with open(outfname, 'w') as outf:
            outf.write('$(function() {\n')
            outf.write('var table = document.createElement("table");\n')
            outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
            outf.write('var header = table.createTHead();\n')
            outf.write('header.className = "h4";\n')
            if data is not None: 
                for li in data:
                    _, pth = os.path.split(li[1])
                    outf.write('var row = table.insertRow(-1);\n')
                    outf.write('var cell = row.insertCell(0);\n')
                    outf.write('cell.innerHTML = "{}";\n'.format(pth))
                    outf.write('var cell = row.insertCell(1);\n')
                    outf.write('cell.innerHTML = "{}";\n'.format(li[2]))
                    outf.write('var cell = row.insertCell(2);\n')
                    outf.write('cell.innerHTML = "{}";\n'.format(li[3]))

            outf.write('var row = header.insertRow(0);\n')
            outf.write('var cell = row.insertCell(0);\n')
            outf.write('cell.innerHTML = "Timestamp";\n')
            outf.write('cell.className = "small";\n')
            outf.write('var cell = row.insertCell(1);\n')
            outf.write('cell.innerHTML = "Shower";\n')
            outf.write('cell.className = "small";\n')
            outf.write('var cell = row.insertCell(2);\n')
            outf.write('cell.innerHTML = "Abs Mag";\n')
            outf.write('cell.className = "small";\n')

            outf.write('var outer_div = document.getElementById("matchlist");\n')
            outf.write('outer_div.appendChild(table);\n')

            outf.write('})\n')

    return


def createWebpage(datadir):
    os.makedirs(os.path.join(datadir, 'browse','daily'), exist_ok=True)
    idxfile = os.path.join(datadir, 'browse/daily/browselist.js')
    with open(idxfile, 'w') as outf:
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = "h4";\n')

        outf.write('var row = table.insertRow(-1);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "<a href=./ukmon-latest.csv>ukmon-latest.csv</a>";\n')

        outf.write('var row = table.insertRow(-1);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "<a href=./cameradetails.csv>cameradetails.csv</a>";\n')

        outf.write('var row = header.insertRow(0);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "File";\n')
        outf.write('cell.className = "small";\n')

        outf.write('var outer_div = document.getElementById("browselist");\n')
        outf.write('outer_div.appendChild(table);\n')

        outf.write('})\n')

    return 


def createCameraFile(datadir):
    ppdir = os.path.join(datadir, 'admin', 'cameraLocs.json')
    pps = json.load(open(ppdir))
    os.makedirs(os.path.join(datadir, 'browse','daily'), exist_ok=True)
    with open(os.path.join(datadir, 'browse/daily/cameradetails.csv'), 'w') as outf:
        outf.write('camera_id,obs_latitude,obs_longitude,obs_az,obs_ev,obs_rot,fov_horiz,fov_vert\n')
        for pp in pps:
            outf.write(pp + ',')
            outf.write('{:.1f},'.format(pps[pp]['lat']))
            outf.write('{:.1f},'.format(pps[pp]['lon']))
            outf.write('{:.1f},'.format(pps[pp]['az']))
            outf.write('{:.1f},'.format(pps[pp]['alt']))
            outf.write('{:.1f},'.format(pps[pp]['rot']))
            outf.write('{:.1f},'.format(pps[pp]['fov_h']))
            outf.write('{:.1f}\n'.format(pps[pp]['fov_v']))
    return


if __name__ == '__main__':
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    if len(sys.argv) > 1:
        targdate = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        targdate = datetime.datetime.now()
        createCameraFile(datadir)
    
    createDetectionsFile(targdate, datadir)
    createMatchesFile(targdate, datadir)
    createWebpage(datadir)
