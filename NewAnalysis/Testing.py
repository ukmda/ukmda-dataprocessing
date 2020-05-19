# testing my shiny new Python classes

import sys, os
import ReadUFOCapXML, ReadUFOAnalyzerXML

if __name__ == '__main__':
    xp='test_data/M20200427_201548_TACKLEY_NE.xml'
    xa='test_data/M20200427_201548_TACKLEY_NEA.xml'

    dd=ReadUFOCapXML.UCXml(xp)

    y,m,d = dd.getDateYMD()
    h,mi,s = dd.getTimeHMS()
    print ('date and time', y,m,d,h,mi,s)

    station, lid, sid, lat, lng,alti=dd.getStationDetails()
    fps, cx, cy = dd.getCameraDetails()
    print('location', station, lat, lng, alti)
    print('camera', fps, cx, cy)

    nhits = dd.getHits()
    for i in range(nhits):
        fno,ono,pixel,bmax,x,y = dd.getPaths(i)
        print(fno,pixel,bmax,x,y)

    dd=ReadUFOAnalyzerXML.UAXml(xa)

    y,m,d = dd.getDateYMD()
    h,mi,s = dd.getTimeHMS()
    print ('date and time', y,m,d,h,mi,s)

    station, lid, sid, lat, lng,alti=dd.getStationDetails()
    fps, cx, cy = dd.getCameraDetails()
    print('location', station, lat, lng, alti)
    print('camera', fps, cx, cy)
    az, ev, rot, fovh, yx, dx, dy, lnk=dd.getProfDetails()
    print('profile',az, ev, rot, fovh, yx, dx, dy, lnk)

    nobjs = dd.getObjectCount()
    for i in range(nobjs):
        sec, av, pix, bmax, mag, fcount=dd.getObjectBasics(i)
        ra1, dc1, h1, dist1, lng1, lat1 = dd.getObjectStart(i)
        ra2, dc2, h2, dist2, lng2, lat2 = dd.getObjectEnd(i)
        print(sec, ra1, dc1, h1, dist1, lng1, lat1, ra2, dc2, h2, dist2, lng2, lat2)
        print (fcount)
        print ('fno', 'ra', 'dec', 'mag', 'az', 'ev', 'lsum', 'b')
        for j in range(fcount):
            fno, ra, dec, mag, az, ev, lsum, b = dd.getObjectFrameDetails(i,j)
            print (fno, ra, dec, mag, az, ev, lsum, b)
 