# tests for createExchangeFiles.py
import datetime
import os

from reports.CameraDetails import getCamLocDirFov, updateCamLocDirFovDB, SiteInfo

here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.path.join(here, 'data')
targdate = datetime.datetime(2023,5,12)


def test_updateCamLocDirFovDB():
    updateCamLocDirFovDB(datadir)
    csvf = os.path.join(datadir, 'admin', 'cameraLocs.json')
    assert os.path.isfile(csvf)
    dets = getCamLocDirFov('UK0006')
    assert abs(dets['lat']-51.8831) < 0.001
    os.remove(csvf)


def test_SiteInfo():
    camfile = os.path.join(datadir, 'consolidated', 'camera-details.csv')
    si = SiteInfo(fname=camfile)
    assert si.GetSiteLocation('UK0006') == 'Tackley/UK0006'
    assert si.GetSiteLocation('UK0000') == 'unknown'
    assert si.getDummyCode('Tackley', 'NE') == 'UK9971'
    assert si.getDummyCode('Tackley', 'XX') == 'Unknown'
    assert si.getFolder('UK0006') == 'Tackley/UK0006'
    assert si.getFolder('UK0000') == 'Unknown'
    assert si.checkCameraActive('UK0006') == 1
    assert si.checkCameraActive('UK0000') == 0
    assert si.getCameraOffset('UK0006') == 6
    assert si.getCameraOffset('UK0000') == -1
    assert si.getCameraLocAndDir('UK0006', activeonly=True) == 'Tackley_SW'
    assert si.getCameraType('UK0006') == 2
    assert si.getCameraType('UK0000') == -1

    cams = si.getActiveCameras()
    match = 0
    for cam in cams:
        if b'Tackley' in cam:
            match = 1
    assert match == 1

    cams, fldrs = si.getAllCamsAndFolders()
    assert 'UK000C' in cams
    assert 'Ash_Vale/UK000C' in fldrs
    cams, fldrs = si.getAllCamsAndFolders(isactive=True)
    assert 'UK0006' in cams
    assert 'Tackley/UK0006' in fldrs

    locsstr = si.getAllLocsStr(onlyActive=False)
    assert 'Ash_Vale' in locsstr
    locsstr = si.getAllLocsStr(onlyActive=True)
    assert 'Tackley' in locsstr

    locsstr = si.getAllCamsStr(onlyActive=False)
    assert 'Ash_Vale' in locsstr
    locsstr = si.getAllCamsStr(onlyActive=True)
    assert 'UK0006' in locsstr


    stats = si.getStationsAtSite('Tackley', onlyactive=False)
    assert 'UK0006' in stats
    stats = si.getStationsAtSite('Tackley', onlyactive=True)
    assert 'UK000C' not in stats
    stats = si.getStationsAtSite('Froboxx', onlyactive=False)
    assert stats == []

    sites = si.getSites(onlyactive=True)
    assert 'Tackley' in sites
    sites = si.getSites(onlyactive=False)
    assert 'Ash_Vale' in sites

    ufos = si.getUFOCameras(onlyactive=True)
    assert ufos == []
    ufos = si.getUFOCameras(onlyactive=False)
    print(ufos)
    match = 0
    for cam in ufos:
        if 'Scotch-Street' in cam['Site']:
            match = 1
    assert match == 1
