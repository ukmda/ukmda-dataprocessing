#
# python module to read the IMO Working Shower short List
#

import xmltodict
import datetime
import os
import numpy as np
from wmpl.Utils.TrajConversions import jd2Date
from utils.convertSolLon import sollon2jd

# imported from $SRC/share
import majorminor as mm


class IMOshowerList:

	def __init__(self, fname=None, fullstreamname=None):
		if fname is None:
			datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
			fname = os.path.join(datadir, '..', 'share', 'IMO_Working_Meteor_Shower_List.xml')

		with open(fname) as fd:
			tmplist = xmltodict.parse(fd.read())
			self.showerlist = tmplist['meteor_shower_list']['shower']
			self.fullstreamdata = None

	
	def getShowerByCode(self, iaucode):
		ds = {'@id':None, 'IAU_code':None,'start':None, 'end':None, 
			'peak':None, 'r':None, 'name':None, 'V':None, 'ZHR':None, 'RA':None, 'DE':None }
		got = None
		for shower in self.showerlist:
			if shower['IAU_code'] == iaucode:
				return shower
		if got is None:
		# load stream full dataset as backup
			if self.fullstreamdata is None:
				wmpldir = os.getenv('WMPL_LOC', default='/home/ec2-user/src/WesternMeteorPyLib')
				fullstreamname = os.path.join(wmpldir, 'wmpl', 'share', 'streamfulldata.npy')
				self.fullstreamdata = np.load(fullstreamname)
			subset = self.fullstreamdata[np.where(self.fullstreamdata[:,3]==iaucode)]
			
			if subset is not None:
				mtch = [sh for sh in subset if sh[6] != '-2']
				if len(mtch) > 0:
					ds['IAU_code'] = mtch[-1][3].strip()
					ds['name'] = mtch[-1][4].strip()
					ds['V'] = mtch[-1][12]
					ds['@id'] = mtch[-1][1]
					ds['RA'] = mtch[-1][8]
					ds['DE'] = mtch[-1][9]

					pksollong = float(mtch[-1][7])
					dt = datetime.datetime.now()
					yr = dt.year
					mth = dt.month
					jd = sollon2jd(yr, mth, pksollong)
					pkdt = jd2Date(jd, dt_obj=True)
					ds['peak'] = pkdt.strftime('%h %d')
					# start/end pop idx, ZHR not available in the IAU data
					ds['start'] = (pkdt + datetime.timedelta(days=-2)).strftime('%h %d')
					ds['end'] = (pkdt + datetime.timedelta(days=2)).strftime('%h %d')
					ds['r'] = '2.0'
					ds['ZHR'] = '3.0' 
		return ds

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
