#  A class to handle UFO Analyser xml files

import sys
import xmltodict
import datetime
import math
import numpy


class UAXml:
    def __init__(self, fname):
        """Construct the object from a filename

        Arguments:
            fname string -- The full path and filename to the XML file
        """
        with open(fname) as fd:
            self.uaxml = xmltodict.parse(fd.read())

    def getDateTime(self):
        y, m, d = UAXml.getDateYMD(self)
        h, mi, s = UAXml.getTimeHMS(self)
        ss = int(math.floor(s))
        ms = int((s - ss) * 1000000)

        dtim = datetime.datetime(y, m, d, h, mi, ss, ms)
        return dtim

    def getDate(self):
        """ Get the event date as an int

        Returns:
            int -- date as YYYYMMDD
        """
        ur = self.uaxml['ufoanalyzer_record']
        return int(ur['@y']) * 10000 + int(ur['@mo']) * 100 + int(ur['@d'])

    def getDateYMD(self):
        """Get the event date as a tuple y,n,d

        Returns:
            int -- year
            int -- month
            int -- day
        """
        yr = int(self.uaxml['ufoanalyzer_record']['@y'])
        mo = int(self.uaxml['ufoanalyzer_record']['@mo'])
        dy = int(self.uaxml['ufoanalyzer_record']['@d'])
        return yr, mo, dy

    def getDateStr(self):
        """get the event date as a string
        Returns:
            string -- YYYY-MM-DD
        """
        ur = self.uaxml['ufoanalyzer_record']
        return ur['@y'] + "-" + ur['@mo'] + "-" + ur['@d']

    def getTime(self):
        """Get the time as a number of seconds since midnight

        Returns:
            int -- secs
        """
        ur = self.uaxml['ufoanalyzer_record']
        return int(ur['@h']) * 3600 + int(ur['@m']) * 60 + float(ur['@s'])

    def getTimeStr(self):
        """Get time as a string

        Returns:
            string -- hh:mm:ss.sss
        """
        ur = self.uaxml['ufoanalyzer_record']
        return ur['@h'] + ":" + ur['@m'] + ":" + ur['@s']

    def getTimeHMS(self):
        """Get time as H,M and S

        Returns:
            int -- hour
            int -- minute
            float -- seconds and milliseconds
        """
        h = int(self.uaxml['ufoanalyzer_record']['@h'])
        m = int(self.uaxml['ufoanalyzer_record']['@m'])
        s = float(self.uaxml['ufoanalyzer_record']['@s'])
        return h, m, s

    def getCameraDetails(self):
        """Get basic camera details

        Returns:
            float -- frames per second
            float -- horizontal resolution cx
            float -- vertical resolution cy
        """
        fps = float(self.uaxml['ufoanalyzer_record']['@fps'])
        cx = float(self.uaxml['ufoanalyzer_record']['@cx'])
        cy = float(self.uaxml['ufoanalyzer_record']['@cy'])
        isintl = int(self.uaxml['ufoanalyzer_record']['@interlaced'])
        return fps, cx, cy, isintl

    def getStationDetails(self):
        """Get station details

        Returns:
            string -- station name eg TACKLEY_TC
            string -- LID eg TACKLEY
            string -- SID eg TC
            float -- latitude
            float -- longitude (W negative)
            float -- altitude (metres)
        """
        sta = self.uaxml['ufoanalyzer_record']['@lid'] + "_" + self.uaxml['ufoanalyzer_record']['@sid']
        lid = self.uaxml['ufoanalyzer_record']['@lid']
        sid = self.uaxml['ufoanalyzer_record']['@sid']
        lat = float(self.uaxml['ufoanalyzer_record']['@lat'])
        lng = float(self.uaxml['ufoanalyzer_record']['@lng'])
        alt = float(self.uaxml['ufoanalyzer_record']['@alt'])
        return sta, lid, sid, lat, lng, alt

    def getProfDetails(self):
        """Get details of the profile used to determine the track

        Returns:
            float -- azimuth, elevation and rotation
            float -- horizontal field of view in degrees
            float -- yx, dz, dy (some fit parameters)
            float -- number of linked stars
        """
        az = float(self.uaxml['ufoanalyzer_record']['@az'])
        ev = float(self.uaxml['ufoanalyzer_record']['@ev'])
        rot = float(self.uaxml['ufoanalyzer_record']['@rot'])
        fovh = float(self.uaxml['ufoanalyzer_record']['@vx'])
        yx = float(self.uaxml['ufoanalyzer_record']['@yx'])
        dx = float(self.uaxml['ufoanalyzer_record']['@dx'])
        dy = float(self.uaxml['ufoanalyzer_record']['@dy'])
        lnk = float(self.uaxml['ufoanalyzer_record']['@dl'])
        return az, ev, rot, fovh, yx, dx, dy, lnk

    def getObjectCount(self):
        """Returns the number of objects in this file

        Returns:
            int - number of objects
        """
        return int(self.uaxml['ufoanalyzer_record']['@o'])

    def getObjectBasics(self, objno):
        """Get basic details about an object

        Arguments:
            objno int -- the object number zero based

        Returns:
            float -- duration in seconds
            float -- angular velocity
            int -- pix count
            float -- max brightness
            float -- magnitude estimate
            int -- number of frames with a moving object in
        """
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        sec = float(uo['@sec'])
        av = float(uo['@av'])
        pix = int(uo['@pix'])
        bmax = float(uo['@bmax'])
        mag = float(uo['@mag'])
        fcount = int(uo['@sN'])
        return sec, av, pix, bmax, mag, fcount

    def getObjectStart(self, objno):
        """Get the details of the start point of an object

        Arguments:
            objno int -- object to retrieve

        Returns:
            floats - ra, dec, height, distance, latitude and longitude
        """
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        ra1 = uo['@ra1']
        dc1 = uo['@dc1']
        h1 = uo['@h1']
        dist1 = uo['@dist1']
        lng1 = uo['@lng1']
        lat1 = uo['@lat1']
        return ra1, dc1, h1, dist1, lng1, lat1

    def getObjectEnd(self, objno):
        """Get the details of the end point of an object

        Arguments:
            objno int -- object to retrieve

        Returns:
            floats - ra, dec, height, distance, latitude and longitude
        """
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        ra2 = uo['@ra2']
        dc2 = uo['@dc2']
        h2 = uo['@h2']
        dist2 = uo['@dist2']
        lng2 = uo['@lng2']
        lat2 = uo['@lat2']
        return ra2, dc2, h2, dist2, lng2, lat2

    def getObjectFrameDetails(self, objno, fno):
        """Get details of a specific frame

        Arguments:
            objno int -- object number
            fno int -- frame number

        Returns:
            float -- frame no,ra, dec, magnitude, az, ev, total brightness
            int -- b
        """
        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = int(self.uaxml['ufoanalyzer_record']['@o'])
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        uop = uo['ua2_objpath']['ua2_fdata2'][fno]
        fno = int(uop['@fno'])
        b = int(uop['@b'])
        lsum = float(uop['@Lsum'])
        mag = float(uop['@mag'])
        az = float(uop['@az'])
        ev = float(uop['@ev'])
        ra = float(uop['@ra'])
        dec = float(uop['@dec'])
        return fno, ra, dec, mag, az, ev, lsum, b

    def getPathVector(self, objno, equat=True):
        fps, _, _, isintl = UAXml.getCameraDetails(self)
        dtim = UAXml.getDateTime(self)

        uos = self.uaxml['ufoanalyzer_record']['ua2_objects']
        oc = UAXml.getObjectCount(self)
        if oc == 1:
            uo = uos['ua2_object']
        else:
            uo = uos['ua2_object'][objno]
        fcount = int(uo['@sN'])
        fno = numpy.zeros(fcount)
        ra = numpy.zeros(fcount)
        dec = numpy.zeros(fcount)
        tt = numpy.zeros(fcount)
        mag = numpy.zeros(fcount)
        for fc in range(fcount):
            uop = uo['ua2_objpath']['ua2_fdata2'][fc]
            fno[fc] = int(uop['@fno'])
            if equat == 1:
                ra[fc] = float(uop['@ra'])
                dec[fc] = float(uop['@dec'])
            else:
                ra[fc] = float(uop['@az'])
                dec[fc] = float(uop['@ev'])
            mag[fc] = float(uop['@mag'])

            # UFO timestamps the 32nd frame for unknown reasons
            us = int((fno[fc]-32) / fps * 1000000)
            tt[fc] = round((dtim + datetime.timedelta(microseconds=us)).timestamp(), 2)
        return fno, tt, ra, dec, mag, fcount


if __name__ == '__main__':
    dd = UAXml(sys.argv[1])

    dtim = dd.getDateTime()

    station, lid, sid, lat, lng, alti = dd.getStationDetails()
    fps, cx, cy, isintl = dd.getCameraDetails()
    print('location', station, lat, lng, alti)
    print('date ', dtim, '\nand path')
    if isintl == 1:
        fps = fps * 2
    # print('camera', fps, cx, cy)
    # az, ev, rot, fovh, yx, dx, dy, lnk = dd.getProfDetails()
    # print('profile', az, ev, rot, fovh, yx, dx, dy, lnk)

    nobjs = dd.getObjectCount()
    for i in range(nobjs):
        # sec, av, pix, bmax, mag, fcount = dd.getObjectBasics(i)
        # ra1, dc1, h1, dist1, lng1, lat1 = dd.getObjectStart(i)
        # ra2, dc2, h2, dist2, lng2, lat2 = dd.getObjectEnd(i)
        # print(sec, ra1, dc1, h1, dist1, lng1, lat1, ra2, dc2, h2, dist2, lng2, lat2)
        # print(fcount)
        # print('fno', 'ra', 'dec', 'mag', 'az', 'ev', 'lsum', 'b')
        # for j in range(fcount):
        #     fno, ra, dec, mag, az, ev, lsum, b = dd.getObjectFrameDetails(i, j)
        #     us = int(fno / fps * 1000000)
        #     tt = dtim + datetime.timedelta(microseconds=us)
        #     print(tt, fno, ra, dec, mag, az, ev, lsum, b)
        fno, tt, ra, dec, fcount = dd.getPathVector(i)
        for j in range(fcount):
            print(datetime.datetime.fromtimestamp(tt[j]), ra[j], dec[j], fno[j])
