# tests for createExchangeFiles.py
import datetime
import os
import shutil

from reports.createExchangeFiles import createDetectionsFile, createMatchesFile, \
    createWebpage, createCameraFile

here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.path.join(here, 'data')
targdate = datetime.datetime(2023,5,12)


def test_createDetectionsFile():
    createDetectionsFile(targdate, datadir)
    csvf = os.path.join(datadir, 'browse','daily', 'ukmon-latest.csv')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert lis[9] == 'UK0020,2023-05-11T22:57:41.534592,\n'
    os.remove(csvf)
    csvf = os.path.join(datadir, 'browse','daily', 'eventlist.js')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert lis[9] == 'cell.innerHTML = "2023-05-11T22:59:50.648359";\n'
    os.remove(csvf)


def test_createMatchesFile():
    createMatchesFile(targdate, datadir)
    csvf = os.path.join(datadir, 'browse','daily', 'matchlist.js')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert lis[9] == 'cell.innerHTML = "ELY";\n'
    os.remove(csvf)


def test_createCameraFile():
    opf = os.path.join(datadir, 'admin','cameraLocs.json.full')
    tpf = os.path.join(datadir, 'admin','cameraLocs.json')
    shutil.copyfile(opf, tpf)
    createCameraFile(datadir)
    csvf = os.path.join(datadir, 'browse','daily', 'cameradetails.csv')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert lis[0] == 'camera_id,obs_latitude,obs_longitude,obs_az,obs_ev,obs_rot,fov_horiz,fov_vert\n'
    os.remove(csvf)
    os.remove(tpf)


def test_createWebpage():
    createWebpage(datadir)
    csvf = os.path.join(datadir, 'browse','daily', 'browselist.js')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert lis[7] == 'cell.innerHTML = "<a href=./ukmon-latest.csv>ukmon-latest.csv</a>";\n'
    os.remove(csvf)
