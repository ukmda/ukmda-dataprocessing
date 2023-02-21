# tests for usertools
import os
import simplekml

from usertools.getOverlappingFovs import getOverlapWith
from usertools.toKML import getTrajPickle, getTrackDetails, trackCsvtoKML
from usertools.retrieveECSV import getECSVs

def test_fovchecker():
    srcfolder = './kmls'
    kmlpat='*-70km.kml'
    refcam = 'UK008A'
    overlaps = getOverlapWith(srcfolder, kmlpat, refcam)
    print(overlaps)
    expected = ['UK008A', 'IE000J', 'UK0003', 'UK000B', 'UK000C', 
                'UK000P', 'UK003B', 'UK004U', 'UK004V', 'UK0052', 
                'UK0056', 'UK0057', 'UK005J', 'UK005K', 'UK0061', 
                'UK0066', 'UK006C', 'UK006E', 'UK006J', 'UK006T', 'UK0073', 
                'UK007G', 'UK007J', 'UK007Y', 'UK0085', 'UK0087', 'UK0088']
    assert (overlaps == expected)


def test_toKML():
    orbname = '20230202_014115.520_UK'
    traj, kmlfile = getTrajPickle(orbname)
    tdets = getTrackDetails(traj)
    kmlfile = os.path.join('usertools', kmlfile)
    os.makedirs('usertools', exist_ok=True)
    trackCsvtoKML(kmlfile, tdets)
    orig = open(os.path.join('usertools','20230202_014115_baseline.kml')).readlines()
    newf = open(os.path.join('usertools','20230202_014115.kml')).readlines()
    assert(orig == newf)


def test_getECSVs():
    stat ='UK0025'
    dt = '2021-07-17T02:41:05.05'
    getECSVs(stat, dt, savefiles=True, outdir='usertools' )
    orig = open(os.path.join('usertools','2021-07-17T02_41_05_05_M004_baseline.ecsv')).readlines()
    newf = open(os.path.join('usertools','2021-07-17T02_41_05_05_M004.ecsv')).readlines()
    assert(orig == newf)

