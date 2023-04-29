from ukmon_meteortools.fileformats import filterFTPforSpecificTime
from ukmon_meteortools.fileformats import IMOshowerList, majorlist, minorlist
from ukmon_meteortools.fileformats import loadPlatepars
from ukmon_meteortools.fileformats import UAXml, UCXml

import shutil
import filecmp
import os

here = os.path.split(os.path.abspath(__file__))[0]


# loadFTPDetectInfo and writeNewFTPFile are also tested by this
def test_filterFTPforSpecificTime():
    srcftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.orig')
    ftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt')
    oldftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.old')
    shutil.copy(srcftpfile, ftpfile)
    dtstr = '20230112_210240'
    newname, nummets = filterFTPforSpecificTime(ftpfile, dtstr)
    print(newname)
    assert nummets == 1
    assert filecmp.cmp(oldftpfile, srcftpfile) is True
    lis = open(newname, 'r').readlines()
    assert lis[0] == 'Meteor Count = 000001\n'
    os.remove(ftpfile)
    os.remove(oldftpfile)
    

def test_IMOShowerList():
    iwsl = IMOshowerList()
    shwr = iwsl.getShowerByCode('PER')
    assert shwr['IAU_code'] == 'PER'


def test_MajMin():
    assert majorlist[0] == 'QUA'
    assert minorlist[0] == 'SPE'
    

def test_loadPlatepars():
    fldr = os.path.join(here, 'data')
    pps = loadPlatepars(fldr)
    assert pps['UK0006']['station_code'] == 'UK0006'


def test_loadUFOCapFormat():
    uc = UCXml(os.path.join(here, 'data', 'ucexample.xml'))
    sta, lid, sid, lat, lng, alt = uc.getStationDetails()
    assert sta == 'TACKLEY_TC'


def test_loadUFOAnalyserFormat():
    ua = UAXml(os.path.join(here, 'data', 'uaexample.xml'))
    fps, cx, cy, isintl = ua.getCameraDetails()
    assert fps == 25.0
