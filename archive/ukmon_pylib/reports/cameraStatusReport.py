#
# create report of last update date by camera. 
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import reports.CameraDetails as cc
import datetime
import pandas as pd 


def getLastUpdateDate():
    """ Create a status report showing the last update date of each camera that
    is providing data

    Args:
        pth (str): path containing the camera data folders
        skipfldrs (list): list of folders to ignore eg ['trajectories','dailyreports']
        includenever (bool) default false, include cameras that have never uploaded
        
    """
    camdets = cc.SiteInfo()
    cams = camdets.getActiveCameras()
    sites=[]
    ids = []
    for c in cams:
        sites.append(c['Site'].decode('utf-8'))
        ids.append(c['CamID'].decode('utf-8'))
    caminfo = pd.DataFrame(zip(sites,ids), columns=['Site','stationid'])

    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    fldrlist = pd.read_csv(os.path.join(datadir,'reports','camuploadtimes.csv'), index_col=False)

    now = datetime.datetime.now()
    fldrlist['isactive'] = [camdets.checkCameraActive(f) for f in fldrlist.stationid]
    fldrlist = fldrlist[fldrlist.isactive is True]
    fldrlist.rundate.fillna(fldrlist.upddate.astype(str) + '_' + fldrlist.uploadtime.astype(str).str.pad(width=6,fillchar='0'), inplace=True)
    fldrlist['dtstamp'] = [datetime.datetime.strptime(f,'%Y%m%d_%H%M%S') for f in fldrlist.rundate]
    fldrlist = fldrlist.sort_values(by=['stationid','dtstamp'])
    fldrlist.drop_duplicates(keep='last', subset=['stationid'], inplace=True)
    fldrlist['lateness'] = [(now - f) for f in fldrlist.dtstamp]

    # create a colour column
    fldrlist = fldrlist.assign(colour=fldrlist.rundate)
    # mark status 
    redthresh = datetime.timedelta(days=3)
    amberthresh=datetime.timedelta(hours=36)
    fldrlist.loc[fldrlist.lateness <= amberthresh, 'colour'] = 'white'
    fldrlist.loc[fldrlist.lateness > amberthresh, 'colour'] = 'darkorange'
    fldrlist.loc[fldrlist.lateness > redthresh, 'colour'] = 'lightcoral'
    fldrlist.loc[fldrlist.lateness > datetime.timedelta(days=365), 'colour'] = 'mediumpurple'

    # drop unused columns
    fldrlist = fldrlist.drop(columns=['lateness','dtstamp','isactive','manual', 'upddate','uploadtime'])

    # now add the site name
    fldrlist = fldrlist.merge(caminfo, on=['stationid'])
    fldrlist = fldrlist.sort_values(by=['Site','stationid'])
    
    return fldrlist


def createStatusReportJSfile(stati):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    repfile = os.path.join(datadir, 'reports','camrep.js')
    with open(repfile, 'w') as outf: 
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className="table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = "h4";\n')

        for rw in stati.iterrows():
            s = rw[1] # the tuple of data
            outf.write('var row = table.insertRow(-1);\n')
            outf.write('row.style.backgroundColor="{}";\n'.format(s.colour)) 
            outf.write('var cell = row.insertCell(0);\n')
            outf.write('cell.innerHTML = "{}";\n'.format(s.Site))
            outf.write('var cell = row.insertCell(1);\n')
            outf.write('cell.innerHTML = "{}";\n'.format(s.stationid))
            outf.write('var cell = row.insertCell(2);\n')
            rd = datetime.datetime.strptime(s.rundate, '%Y%m%d_%H%M%S')
            outf.write('cell.innerHTML = "{}";\n'.format(rd.strftime('%Y-%m-%d %H:%M:%S')))

        outf.write('var row = table.insertRow(0);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "Location";\n')
        outf.write('var cell = row.insertCell(1);\n')
        outf.write('cell.innerHTML = "Cam";\n')
        outf.write('var cell = row.insertCell(2);\n')
        outf.write('cell.innerHTML = "Date of Run";\n')
        outf.write('var outer_div = document.getElementById("camrep");\n')
        outf.write('outer_div.appendChild(table);\n')
        outf.write('})\n')
    return 


if __name__ == '__main__':
    stati = getLastUpdateDate()
    createStatusReportJSfile(stati)
