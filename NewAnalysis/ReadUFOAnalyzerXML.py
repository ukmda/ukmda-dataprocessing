# class to handle UFO Analyser xml files

import os, sys
import xmltodict 

class UAXml: 
    def __init__(self, fname):
        with open(fname) as fd:
            self.uaxml=xmltodict.parse(fd.read())
    def getDate(self):
        ur=self.uaxml['ufoanalyzer_record']
        return int(ur['@y'])*10000 + int(ur['@mo'])*100 +int(ur['@d'])
    def getDateYMD(self):
        yr= int(self.uaxml['ufoanalyzer_record']['@y'])
        mo = int(self.uaxml['ufoanalyzer_record']['@mo'])
        dy = int(self.uaxml['ufoanalyzer_record']['@d'])
        return yr,mo,dy
    def getDateStr(self):
        ur=self.uaxml['ufoanalyzer_record']
        return ur['@y']+"-"+ur['@mo']+"-"+ur['@d']

    def getTime(self):
        ur=self.uaxml['ufoanalyzer_record']
        return int(ur['@h'])*3600 + int(ur['@m'])*60 +float(ur['@s'])
    def getTimeStr(self):
        ur=self.uaxml['ufoanalyzer_record']
        return ur['@h'] +":"+ ur['@m']+":" +ur['@s']
    def getTimeHMS(self):
        h = int(self.uaxml['ufoanalyzer_record']['@h'])
        m = int(self.uaxml['ufoanalyzer_record']['@m'])
        s =  float(self.uaxml['ufoanalyzer_record']['@s'])
        return h,m,s

    def getCameraDetails(self):
        fps = float(self.uaxml['ufoanalyzer_record']['@fps'])
        cx  = float(self.uaxml['ufoanalyzer_record']['@cx'])
        cy  = float(self.uaxml['ufoanalyzer_record']['@cy'])
        return fps,cx,cy

    def getStationDetails(self):
        sta = self.uaxml['ufoanalyzer_record']['@lid'] + "_"+self.uaxml['ufoanalyzer_record']['@sid']
        lid = self.uaxml['ufoanalyzer_record']['@lid']
        sid =  self.uaxml['ufoanalyzer_record']['@sid']
        lat = float(self.uaxml['ufoanalyzer_record']['@lat'])
        lng = float(self.uaxml['ufoanalyzer_record']['@lng'])
        alt = float(self.uaxml['ufoanalyzer_record']['@alt'])
        return sta, lid, sid, lat, lng, alt

    def getProfDetails(self):
        az  = float(self.uaxml['ufoanalyzer_record']['@az'])
        ev  = float(self.uaxml['ufoanalyzer_record']['@ev'])
        rot = float(self.uaxml['ufoanalyzer_record']['@rot'])
        fovh= float(self.uaxml['ufoanalyzer_record']['@vx'])
        yx = float(self.uaxml['ufoanalyzer_record']['@yx'])
        dx = float(self.uaxml['ufoanalyzer_record']['@dx'])
        dy = float(self.uaxml['ufoanalyzer_record']['@dy'])
        lnk= float(self.uaxml['ufoanalyzer_record']['@dl'])
        return az, ev, rot, fovh, yx, dx, dy, lnk

    def getObjectCount(self):
        return int(self.uaxml['ufoanalyzer_record']['@o'])

    def getObjectBasics(self, objno):
        uos=self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1 : 
            uo=uos['ua2_object']
        else:
            uo=uos['ua2_object'][objno]
        sec = float(uo['@sec'])
        av = float(uo['@av'])
        pix = int(uo['@pix'])
        bmax = float(uo['@bmax'])
        mag = float(uo['@mag'])
        fcount = int(uo['@sN'])
        return sec, av, pix, bmax, mag, fcount

    def getObjectStart(self, objno):
        uos=self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1 : 
            uo=uos['ua2_object']
        else:
            uo=uos['ua2_object'][objno]
        ra1 = uo['@ra1']
        dc1 = uo['@dc1']
        h1  = uo['@h1']
        dist1= uo['@dist1']
        lng1= uo['@lng1']
        lat1= uo['@lat1']
        return ra1, dc1, h1, dist1, lng1, lat1

    def getObjectEnd(self, objno):
        uos=self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1 : 
            uo=uos['ua2_object']
        else:
            uo=uos['ua2_object'][objno]
        ra2 = uo['@ra2']
        dc2 = uo['@dc2']
        h2  = uo['@h2']
        dist2= uo['@dist2']
        lng2= uo['@lng2']
        lat2= uo['@lat2']
        return ra2, dc2, h2, dist2, lng2, lat2

    def getObjectFrameDetails(self, objno, fno):
        uos=self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1 : 
            uo=uos['ua2_object']
        else:
            uo=uos['ua2_object'][objno]
        uop=uo['ua2_objpath']['ua2_fdata2'][fno]
        fno = int(uop['@fno'])
        b    = int(uop['@b'])
        lsum = float(uop['@Lsum'])
        mag = float(uop['@mag'])
        az  = float(uop['@az'])
        ev  = float(uop['@ev'])
        ra  = float(uop['@ra'])
        dec  = float(uop['@dec'])
        return fno, ra, dec, mag, az, ev, lsum, b

if __name__ == '__main__':
    dd=UAXml('test_data/M20200427_201548_TACKLEY_NEA.XML')

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