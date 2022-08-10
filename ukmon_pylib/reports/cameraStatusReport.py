#
# create report of last update date by camera. 
#

import sys
import os
import fileformats.CameraDetails as cc
import datetime
import numpy
#import glob
import pandas as pd 


def datesortkey(x):
    return x[:15]


def statsortkey(x):
    return x[0]


def getLastUpdateDate(pth, skipfldrs, includenever=False):
    """ Create a status report showing the last update date of each camera that
    is providing data

    Args:
        pth (str): path containing the camera data folders
        skipfldrs (list): list of folders to ignore eg ['trajectories','dailyreports']
        includenever (bool) default false, include cameras that have never uploaded
        
    """
    camdets = cc.SiteInfo()

    fldrlist = next(os.walk(pth))[1]

    stati=[]
    now = datetime.datetime.now()
    for fldr in fldrlist:
        if fldr not in (skipfldrs):
            isactive = camdets.checkCameraActive(fldr)
            if isactive is True:
                info = camdets.getFolder(fldr)
                loc, cam = info.split('/')
                camtype = camdets.getCameraType(fldr)
                flist = os.listdir(os.path.join(pth, fldr))
                if len(flist) == 0: 
                    # camera has never uploaded
                    lastdt = datetime.datetime(1970,1,1)
                    stati.append([loc, cam, lastdt, 'mediumpurple'])
                    continue 
                lastentry = sorted(flist, key=datesortkey)[-1]
                lastdt = datetime.datetime.strptime(lastentry[7:22],'%Y%m%d_%H%M%S')
                lateness = (now - lastdt).days
                if camtype == 1:
                    redthresh = 14
                    amberthresh=7
                else:
                    redthresh = 3
                    amberthresh=1

                if lateness > redthresh:
                    stati.append([loc, cam, lastdt, 'lightcoral'])
                elif lateness > amberthresh:
                    stati.append([loc, cam, lastdt, 'darkorange'])
                else:
                    stati.append([loc, cam, lastdt, 'white'])
                    
    if includenever is True:
        for cam in camdets.getActiveCameras()['dummycode']:
            cam = cam.decode('utf-8')
            if cam not in fldrlist:
                info = camdets.getFolder(cam)
                loc, cam = info.split('/')
                lastdt = datetime.datetime(1970,1,1)
                stati.append([loc, cam, lastdt, 'mediumpurple'])

    stati = numpy.vstack((stati))
    stati = stati[stati[:,1].argsort()]
    stati = stati[stati[:,0].argsort(kind='mergesort')]
    return stati


def createStatusReportJSfile(stati):
    print('$(function() {')
    print('var table = document.createElement("table");')
    print('table.className="table table-striped table-bordered table-hover table-condensed";')
    print('var header = table.createTHead();')
    print('header.className = "h4";')

    for s in stati:
        print('var row = table.insertRow(-1);')
        print('row.style.backgroundColor="{}";'.format(s[3])) 
        print('var cell = row.insertCell(0);')
        print('cell.innerHTML = "{}";'.format(s[0]))
        print('var cell = row.insertCell(1);')
        print('cell.innerHTML = "{}";'.format(s[1]))
        print('var cell = row.insertCell(2);')
        print('cell.innerHTML = "{}";'.format(s[2].strftime('%Y-%m-%d %H:%M:%S')))

    print('var row = table.insertRow(0);')
    print('var cell = row.insertCell(0);')
    print('cell.innerHTML = "Location";')
    print('var cell = row.insertCell(1);')
    print('cell.innerHTML = "Cam";')
    print('var cell = row.insertCell(2);')
    print('cell.innerHTML = "Date of Run";')
    print('var outer_div = document.getElementById("camrep");')
    print('outer_div.appendChild(table);')
    print('})')
    return 


def getNonContributingCameras():
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    pth = '/home/ec2-user/ukmon-shared/matches/RMSCorrelate'
    skipfldrs = ['plots','trajectories','dailyreports']
    cams = getLastUpdateDate(pth, skipfldrs, includenever=True)

    df = pd.DataFrame(cams, columns=['loc','camid','date','colour'])
    missing = df[df.date ==datetime.datetime(1970,1,1)]
    
    owners = pd.read_csv(os.path.join(datadir, 'admin','stationdetails.csv'))
    missingcams = owners.loc[owners['camid'].isin(missing.camid)]
    missingcams = missingcams.sort_values(by=['camid'])
    return missingcams


if __name__ == '__main__':
    stati = getLastUpdateDate(sys.argv[1],['plots','trajectories','dailyreports'])
    createStatusReportJSfile(stati)
