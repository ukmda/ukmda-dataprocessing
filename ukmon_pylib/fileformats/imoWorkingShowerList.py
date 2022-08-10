#
# python module to read the IMO Working Shower short List
#

import xmltodict
import datetime
import os

# imported from $SRC/share
import majorminor as mm


class IMOshowerList:

    def __init__(self, fname=None):
        if fname is None:
            datadir = os.getenv('DATADIR')
            if datadir is None:
                datadir='/home/ec2-user/prod/data'
            fname = os.path.join(datadir, '..', 'share', 'IMO_Working_Meteor_Shower_List.xml')

        with open(fname) as fd:
            tmplist = xmltodict.parse(fd.read())
            self.showerlist = tmplist['meteor_shower_list']['shower']

    def getShowerByCode(self, iaucode):
        for shower in self.showerlist:
            if shower['IAU_code'] == iaucode:
                return shower

    def getStart(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        startdate = datetime.datetime.strptime(shower['start'], '%b %d')
        startdate = startdate.replace(year=now)
        return startdate

    def getEnd(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        if iaucode == 'QUA':
            now = now + 1
        enddate = datetime.datetime.strptime(shower['end'], '%b %d')
        enddate = enddate.replace(year=now)
        return enddate

    def getPeak(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        if iaucode == 'QUA':
            now = now + 1
        enddate = datetime.datetime.strptime(shower['peak'], '%b %d')
        enddate = enddate.replace(year=now)
        return enddate

    def getRvalue(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['r']

    def getName(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['name']

    def getVelocity(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['V']

    def getZHR(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        zhr = shower['ZHR']
        if zhr is None:
            return -1
        else:
            return int(zhr)

    def getRaDec(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return float(shower['RA']), float(shower['DE'])

    def getActiveShowers(self, datetotest, majorOnly=False, inclMinor=False):
        activelist = []
        for shower in self.showerlist:
            shwname = shower['IAU_code']
            yr = datetotest.year
            if shwname == 'QUA':
                yr = yr-1
            start = self.getStart(shwname, yr)
            end = self.getEnd(shwname, yr) + datetime.timedelta(days=3)
            if datetotest > start and datetotest < end:
                if majorOnly is False or (majorOnly is True and shwname in mm.majorlist):
                    activelist.append(shwname)
                elif inclMinor is True and shwname in mm.minorlist:
                    activelist.append(shwname)
        return activelist

    def getMajorShowers(self, includeSpo=False, stringFmt=False):
        majlist = mm.majorlist 
        if includeSpo is True:
            majlist.append('spo')
        if stringFmt is True:
            tmplist = ''
            for shwr in majlist:
                tmplist = tmplist + shwr + ' '
            majlist = tmplist
        return majlist
