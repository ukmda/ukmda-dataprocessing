# Copyright (C) 2018-2023 Mark McIntyre 

# script to scan UKMON live data as it arrives for brightness information

import os
import boto3
from tempfile import mkdtemp
from shutil import rmtree
import datetime


def storeInDDb(evtdets, camdets):
    dtval = evtdets['dtval']
    ffname = evtdets['ffname']
    camid = camdets['camid']

    bmax = evtdets['bmax']
    bave = evtdets['bave']
    bstd = evtdets['bstd']

    # table partition key will be the night of capture
    if dtval.hour < 13:
        partkey = int((dtval - datetime.timedelta(days=1)).strftime('%Y%m%d'))
    else:
        partkey = int(dtval.strftime('%Y%m%d'))
    #table sort key will be the timestamp because we can then easily do a range select
    sortkey = int(dtval.timestamp())

    expdate = int((dtval + datetime.timedelta(days=3)).timestamp())

    ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')   
    response = table.put_item(
        Item={
            'CaptureNight': partkey,
            'Timestamp': sortkey,
            'bmax': bmax, 
            'bave': bave,
            'bstd': bstd,
            'camid': camid,
            'ffname': ffname,
            'ExpiryDate': expdate
        }   
    )    
    #print(response)

    return response['ResponseMetadata']['HTTPStatusCode']


def processXml(event, context):
    record = event['Records'][0]
    fname = record['s3']['object']['key']
    buck = 'ukmon-live'
    s3 = boto3.resource('s3')

    if '.xml' in fname:
        _, barefname = os.path.split(fname)
        tmpdir = mkdtemp()
        xmlname = os.path.join(tmpdir, barefname)
        s3.meta.client.download_file(buck, fname, xmlname)
        lis = open(xmlname, 'r').readlines()
        rmtree(tmpdir)

        li = lis[1]
        spls = li.split(' ')
        yr = int(spls[2][3:-1])
        mt = int(spls[3][4:-1])
        dy = int(spls[4][3:-1])
        hr = int(spls[5][3:-1])
        mi = int(spls[6][3:-1])
        secs = spls[7][3:-1]
        if '.0.' in secs:
            secs = secs[:2] + secs[4:]
        secs = float(secs)

        longi =float(spls[10][5:-1])
        lati = float(spls[11][5:-1])
        alti = float(spls[12][5:-1])
        cx = int(spls[15][4:-1])
        cy = int(spls[16][4:-1])
        fps = float(spls[17][5:-1])
        camid = spls[28][5:-1]
        ffname = spls[30][5:-1]

        li = lis[3]
        spls = li.split()
        bmax = int(spls[4][6:-1])
        fno = int(spls[2][5:-1])

        li = lis[4]
        spls = li.split()
        bave = int(spls[4][6:-1])

        li = lis[5]
        spls = li.split()
        bstd = int(spls[4][6:-1])

        dtval = datetime.datetime(yr, mt, dy, hr, mi, 0) + datetime.timedelta(seconds = (secs + fno/fps))

        camdets = {'camid':camid, 'lati': lati, 'longi': longi, 'alti': alti, 'cx': cx, 'cy': cy, 'fps': fps}
        evtdets={'dtval':dtval, 'fno':fno, 'ffname':ffname, 'bmax':bmax, 'bave':bave, 'bstd':bstd}
        return evtdets, camdets


def lambda_handler(event, context):
    evtdets, camdets = processXml(event, context)
    storeInDDb(evtdets, camdets)


# Test cases. Execute with "pytest ./curateLive.py"

def test_handler():
    event = {'Records': [{'s3':{'object':{'key':'test/M20230403_210231_tackley_sw_UK0006.xml'}}}]}
    evtdets, camdets = processXml(event, False)
    assert evtdets['bmax'] == 75966064
    assert evtdets['bave'] == 75240244
    assert evtdets['bstd'] == 560025
    assert camdets['fps'] == 25.0
    assert camdets['cx'] == 1280


def test_handler2():
    event = {'Records': [{'s3':{'object':{'key':'test/M20230403_205525_tackley_ne_UK002F.xml'}}}]}
    evtdets, camdets = processXml(event, False)
    assert evtdets['bmax'] == 81582881
    assert evtdets['ffname'] == 'FF_UK002F_20230403_205525_195_0112640.fits'
    assert evtdets['dtval'] == datetime.datetime(2023,4,3,20,55,25, 915000)
    assert evtdets['fno'] == 18
    assert camdets['camid'] == 'UK002F'


def test_ddbput():
    event = {'Records': [{'s3':{'object':{'key':'test/M20230403_205525_tackley_ne_UK002F.xml'}}}]}
    evtdets, camdets = processXml(event, False)
    ret = storeInDDb(evtdets, camdets)
    assert ret == 200
