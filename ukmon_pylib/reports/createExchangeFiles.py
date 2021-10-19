import fileformats.UAFormats as uaf 
#import fileformats.CameraDetails as cdd
import datetime
import os
import sys
import csv
import configparser as cfg
from fileformats.platepar import loadPlatepars


def createDetectionsFile(sDate, datadir):
    # read and process the daily event data
    dets=uaf.DetectedCsv(os.path.join(datadir,'UKMON-all-single.csv'))
    data = dets.getExchangeData(sDate)
    
    outfname = os.path.join(datadir, 'browse/daily/ukmon-latest.csv')
    with open(outfname,'w') as outf:
        outf.write('camera_id,datetime,image_URL\n')
        if data is not None:
            for li in data:
                outf.write(li[0] + ',' + li[1] + ',\n')
    createEventList(datadir, data)    
    return


def createEventList(datadir, data):
    idxfile = os.path.join(datadir, 'browse/daily/eventlist.js')
    with open(idxfile, 'w') as outf:
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = "h4";\n')

        if data is not None: 
            for li in data:
                outf.write('var row = table.insertRow(-1);\n')
                outf.write('var cell = row.insertCell(0);\n')
                outf.write('cell.innerHTML = "{}";\n'.format(li[0]))
                outf.write('var cell = row.insertCell(1);\n')
                outf.write('cell.innerHTML = "{}";\n'.format(li[1]))

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


def createMatchesFile(sDate, config):
    # read and process the daily matches file
    datadir = config['config']['datadir']
    matchf = os.path.join(datadir, 'dailyreports/{}.txt'.format(sDate.strftime('%Y%m%d')))
    with open(matchf, 'r') as inf:
        data = csv.reader(inf, delimiter=',')

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


def createCameraFile(config):
    datadir = config['config']['datadir']
    ppdir = os.path.join(config['config']['archdir'],'platepars')
    pps = loadPlatepars(ppdir)
    with open(os.path.join(datadir, 'browse/daily/cameradetails.csv'), 'w') as outf:
        outf.write('camera_id,obs_latitude,obs_longitude,obs_az,obs_ev,obs_rot,fov_horiz,fov_vert\n')
        for pp in pps:
            outf.write(pps[pp]['station_code']+',')
            outf.write('{:.1f},'.format(pps[pp]['lat']))
            outf.write('{:.1f},'.format(pps[pp]['lon']))
            outf.write('{:.1f},'.format(pps[pp]['az_centre']))
            outf.write('{:.1f},'.format(pps[pp]['alt_centre']))
            outf.write('{:.1f},'.format(pps[pp]['rotation_from_horiz']))
            outf.write('{:.1f},'.format(pps[pp]['fov_h']))
            outf.write('{:.1f}\n'.format(pps[pp]['fov_v']))
    return


def uploadFiles(config):
    datadir = config['config']['datadir']
    bucket = config['config']['websitebucket']
    keyf = config['config']['websitekey']
    cmd = 'source {} && aws s3 sync {}/browse/daily/ {}/browse/daily/'.format(keyf, datadir, bucket)
    os.system(cmd)
    return


if __name__ == '__main__':
    srcdir = os.getenv('SRC')
    config = cfg.ConfigParser()
    config.read(os.path.join(srcdir, 'config', 'config.ini'))
    datadir = config['config']['datadir']
    if len(sys.argv) > 1:
        targdate = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        targdate = datetime.datetime.now()
        createCameraFile(config)
    
    createDetectionsFile(targdate, datadir)
    createMatchesFile(targdate, config)
    createWebpage(datadir)
    uploadFiles(config)
