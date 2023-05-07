# tests for usertools
import os

from usertools.getOverlappingFovs import getOverlapWith, pointInsideFov, checkKMLOverlap, getOverlappingCameras
from usertools.plotTrack import trackToDistvsHeight, trackToTimevsVelocity, trackToTimevsHeight
from usertools.getLiveImages import createTxtFile, getFBfiles, getLiveJpgs


here = os.path.split(os.path.abspath(__file__))[0]
trackcsvfile = os.path.join(here, 'data', 'sample_track.csv')
kml1 = os.path.join(here, 'data', 'kmls', 'UK0006-70km.kml')
kml2 = os.path.join(here, 'data', 'kmls', 'UK000S-70km.kml')


def test_getOverlapWith():
    srcfolder = os.path.join(here, 'data', 'kmls')
    kmlpat='*-70km.kml'
    refcam = 'UK008A'
    overlaps = getOverlapWith(srcfolder, kmlpat, refcam)
    assert overlaps[3] == 'UK000B'


def test_pointInsideFov():
    lng = -1.4
    lat = 51.7
    res = pointInsideFov(lng, lat, kml1)
    assert res is False
    res = pointInsideFov(lng, lat, kml2)
    assert res is True


def test_checkKMLOverlap():
    res = checkKMLOverlap(kml1, kml2)
    assert res is True


def test_getOverlappingCameras():
    srcfldr = os.path.join(here, 'data', 'kmls')
    res = getOverlappingCameras(srcfldr, '*-70km.kml')
    assert res[0][3]=='UK000P'


def test_trackToDistvsHeight():
    trackToDistvsHeight(trackcsvfile)
    outname = trackcsvfile.replace('.csv','_dist_alt.png')
    assert os.path.isfile(outname)
    os.remove(outname)


def test_trackToTimevsVelocity():
    trackToTimevsVelocity(trackcsvfile)
    outname = trackcsvfile.replace('.csv','_tim_vel.png')
    assert os.path.isfile(outname)
    os.remove(outname)


def test_trackToTimevsHeight():
    trackToTimevsHeight(trackcsvfile)
    outname = trackcsvfile.replace('.csv','_time_alt.png')
    assert os.path.isfile(outname)
    os.remove(outname)


def test_createTxtFile():
    patt = 'FF_UK0006_20230506_210101'
    outdir = os.path.join(here,'data')
    createTxtFile(patt, outdir)
    outfname = os.path.join(outdir, 'uk0006.txt')
    assert os.path.isfile(outfname)
    os.remove(outfname)


def test_createTxtFileHere():
    patt = 'FF_UK0006_20230506_210101'
    outdir = None
    createTxtFile(patt, outdir)
    outfname = 'uk0006.txt'
    assert os.path.isfile(outfname)
    os.remove(outfname)


def test_createTxtFileMtype():
    patt = 'M20230506_210101_foobar_UK0007'
    outdir = os.path.join(here,'data')
    createTxtFile(patt, outdir)
    outfname = os.path.join(outdir, 'uk0007.txt')
    assert os.path.isfile(outfname)
    os.remove(outfname)
