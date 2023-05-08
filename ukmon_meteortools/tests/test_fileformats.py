from fileformats import filterFTPforSpecificTime
from fileformats import IMOshowerList, majorlist, minorlist
from fileformats import loadPlatepars
from fileformats import UAXml, UCXml
from fileformats import readCameraKML, trackCsvtoKML, trackKMLtoCsv #, getTrackDetails

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
    nhits = uc.getHits()
    assert nhits == 22
    fno, ono, pixel, bmax, x, y = uc.getPathElement(1)
    assert fno == '30'


def test_loadUFOAnalyserFormat():
    ua = UAXml(os.path.join(here, 'data', 'uaexample.xml'))
    fps, cx, cy, isintl = ua.getCameraDetails()
    assert fps == 25.0
    assert ua.getObjectCount() == 1
    sec, av, pix, bmax, mag, fcount = ua.getObjectBasics(1)
    assert abs(sec - 0.78) < 0.001
    assert fcount == 40
    assert abs(bmax - 213.0) < 0.1
    assert abs(mag - (-2.66)) < 0.01
    fno, ra, dec, mag, az, ev, lsum, b = ua.getObjectFrameDetails(1, 3)
    assert fno == 61
    assert b == 138


def test_readCameraKML():
    kmlfile = os.path.join(here, 'data','UK0006-70km.kml')
    kml = readCameraKML(kmlfile, True)
    assert kml[0]=='UK0006'


def test_trackCsvtoKML():
    srcfile = os.path.join(here, 'data','sample_track.csv')
    kml = trackCsvtoKML(srcfile)
    assert 'sample_track' in kml.document.name 
    os.remove(os.path.join(here, 'data','sample_track.kml'))


def test_trackKMLtoCsvSave():
    srcfile = os.path.join(here, 'data','sample_track2.kml')
    df = trackKMLtoCsv(srcfile)
    assert abs(df['lats'][0] - 49.922338) < 0.0001
    assert os.path.isfile(os.path.join(here, 'data','sample_track2.csv'))
    os.remove(os.path.join(here, 'data','sample_track2.csv'))


def test_trackKMLtoCsvNoSave():
    srcfile = os.path.join(here, 'data','sample_track2.kml')
    df = trackKMLtoCsv(srcfile, saveOutput=False)
    assert abs(df['lats'][0] - 49.922338) < 0.0001
