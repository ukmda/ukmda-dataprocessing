#
# create report of last update date by camera. 
#

import sys
import os
import fileformats.CameraDetails as cc
import datetime
import numpy


def datesortkey(x):
    return x[:15]


def statsortkey(x):
    return x[0]


def getLastUpdateDate(pth, skipfldrs):
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
                    stati.append([loc, cam, lastdt, 'red'])
                elif lateness > amberthresh:
                    stati.append([loc, cam, lastdt, 'amber'])
                else:
                    stati.append([loc, cam, lastdt, 'green'])
    stati = numpy.vstack((stati))
    stati = stati[stati[:,1].argsort()]
    stati = stati[stati[:,0].argsort(kind='mergesort')]
    print('<style type="text/css">')
    print('table tr#REDROW  {background-color:red; color:white;}')
    print('table tr#AMBERROW  {background-color:darkorange; color:white;}')
    print('</style><table border=\"1\">')
    for s in stati:
        if s[3] =='red':
            print('<tr id=\'REDROW\'><td>{}</td><td>{}</td><td>{}</td></tr>'.format(s[0], s[1], s[2].strftime('%Y-%m-%d')))
        elif s[3] =='amber':
            print('<tr id=\'AMBERROW\'><td>{}</td><td>{}</td><td>{}</td></tr>'.format(s[0], s[1], s[2].strftime('%Y-%m-%d')))
        else:
            print('<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(s[0], s[1], s[2].strftime('%Y-%m-%d')))
    print('</table>')


if __name__ == '__main__':
    getLastUpdateDate(sys.argv[1],['plots','trajectories','dailyreports'])
