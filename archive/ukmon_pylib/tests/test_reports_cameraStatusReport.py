# Copyright (C) 2018-2023 Mark McIntyre
# tests for cameraStatusReport

import datetime
import os
import boto3

from reports.cameraStatusReport import getLastUpdateDate, createStatusReportJSfile


here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('DATADIR', default=os.path.join(here, 'data'))
targdate = datetime.datetime(2023,5,12)


def test_createStatusReportJSfile():
    # for testing we should precreate the DDB connection using the default role
    conn = boto3.Session()
    ddb = conn.resource('dynamodb', region_name='eu-west-2') 

    stati = getLastUpdateDate(datadir=datadir, ddb=ddb)
    assert 'UK0006' in list(stati.stationid)
    createStatusReportJSfile(stati, datadir)
    csvf = os.path.join(datadir, 'reports', 'camrep.js')
    assert os.path.isfile(csvf)
    lis = open(csvf, 'r').readlines()
    assert 'cell.innerHTML = "20' in lis[12]
    os.remove(csvf)
