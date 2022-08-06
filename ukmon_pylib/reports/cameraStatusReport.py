#
# create report of last update date by camera. 
#

import sys
import os
import fileformats.CameraDetails as cc
import datetime
import numpy
import glob
import pandas as pd 


def datesortkey(x):
    return x[:15]


def statsortkey(x):
    return x[0]


def getLastUpdateDate(pth, skipfldrs):
    """ Create a status report showing the last update date of each camera that
    is providing data

    Args:
        pth (str): path containing the camera data folders
        skipfldrs (list): list of folders to ignore eg ['trajectories','dailyreports']
        
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
                camtype = camdets.getCameraType(fldr)
                flist = os.listdir(os.path.join(pth, fldr))
                if len(flist) == 0: 
                    continue 
                lastentry = sorted(flist, key=datesortkey)[-1]
                loc, cam = info.split('/')
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
    stati = numpy.vstack((stati))
    stati = stati[stati[:,1].argsort()]
    stati = stati[stati[:,0].argsort(kind='mergesort')]
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
    si = cc.SiteInfo()
    activecams = si.getActiveCameras()
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    platepars = glob.glob(os.path.join(datadir,'consolidated','platepars','*.json'))
    cams = []
    for pp in platepars:
        _, fn = os.path.split(pp)
        cams.append(os.path.splitext(fn)[0])
    allcams = []
    for cam in activecams:
        allcams.append(cam['CamID'].decode('utf-8'))
    missing=list(set(allcams).difference(cams))
    owners = pd.read_csv(os.path.join(datadir, 'admin','stationdetails.csv'))
    missingcams = owners.loc[owners['camid'].isin(missing)]
    missingcams = missingcams.sort_values(by=['camid'])
    return missingcams


if __name__ == '__main__':
    getLastUpdateDate(sys.argv[1],['plots','trajectories','dailyreports'])
