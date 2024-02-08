# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import os
import boto3
import shutil

from reports.CameraDetails import getCamLocDirFov, updateCamLocDirFovDB
from reports.CameraDetails import loadLocationDetails, findEmail, findSite

here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('TMP')
targdate = datetime.datetime(2023,5,12)


def test_updateCamLocDirFovDB():
    os.makedirs(os.path.join(datadir,'admin'))
    updateCamLocDirFovDB(datadir)
    csvf = os.path.join(datadir, 'admin', 'cameraLocs.json')
    assert os.path.isfile(csvf)
    dets = getCamLocDirFov('UK001M')
    assert abs(dets['lat']-53.31249) < 0.001
    dets = getCamLocDirFov('UK9999')
    assert dets is False
    shutil.rmtree(os.path.join(datadir,'admin'))


def test_loadLocationDetails():
    conn = boto3.Session(profile_name='ukmonshared')
    ddb = conn.resource('dynamodb', region_name='eu-west-2') 
    caminfo = loadLocationDetails(ddb=ddb)
    caminfo = caminfo[caminfo.stationid=='UK0006']
    assert len(caminfo) == 1

    em = findEmail('UK0006', caminfo)
    assert em == 'markmcintyre99@googlemail.com'

    em = findSite('UK0006', caminfo)
    assert em == 'Tackley'
