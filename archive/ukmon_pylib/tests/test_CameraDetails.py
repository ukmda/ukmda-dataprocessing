# tests for createExchangeFiles.py
import datetime
import os

from reports.CameraDetails import getCamLocDirFov, updateCamLocDirFovDB

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
