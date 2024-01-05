# Copyright (C) 2018-2023 Mark McIntyre
# tests for cameraStatusReport

import datetime
import os

from reports.cameraStatusReport import getLastUpdateDate, createStatusReportJSfile


here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('DATADIR', default=os.path.join(here, 'data'))
targdate = datetime.datetime(2023,5,12)


def test_createStatusReportJSfile():
    camfile = os.path.join(datadir, 'consolidated', 'camera-details.csv')
    stati = getLastUpdateDate(datadir, camfile)
    assert 'UK0006' in list(stati.stationid)
    createStatusReportJSfile(stati, datadir)
    csvf = os.path.join(datadir, 'reports', 'camrep.js')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert 'cell.innerHTML = "20' in lis[12]
    os.remove(csvf)
