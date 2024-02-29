#
# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import json
import requests 
import pandas as pd


def test_getMatches():
    reqtyp = 'matches'
    reqval = '20230721'
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}'
    matchlist = pd.read_json(apicall, lines=True)   
    assert len(matchlist) != 339
    assert matchlist.orbname[0] == '20230721_000106.311_UK'


def test_getMatchDetail():
    reqtyp = 'detail'
    reqval = '20230821_000021.339_UK'
    """ get details of one matched event """
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}'
    try:
        df = pd.read_json(apicall, typ='series')
        assert df['_localtime'] == '_20230821_000021' 
    except Exception as e:
        print(repr(e))
        assert False


def test_getMatchPoints():
    reqtyp = 'detail'
    reqval = '20211121_032219.699_UK'
    """ get the points used by one matched event """
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}&points=1'
    try:
        df = pd.read_json(apicall)
        assert df['points'][0]['lon']=='-0.476601'
        assert df['points'][0]['amag']=='+0.68'
    except Exception as e:
        print(repr(e))
        assert False


def test_getMatchPickle():
    patt = '20220814_205940.252_UK'
    apiurl = 'https://api.ukmeteors.co.uk/pickle/getpickle'
    apicall = f'{apiurl}?reqval={patt}'
    res = requests.get(apicall, stream=True)
    if res.status_code == 200:
        data=b''
        for chunk in res.iter_content(chunk_size=4096):
            data = data + chunk
        jsd = json.loads(data)
        assert len(jsd) == 62
        assert len(jsd['observations']) == 5
    else:
        assert False


def test_getLiveImages():
    dtstr = datetime.datetime.now().strftime('%Y%m%d') + '_01'
    apiurl = 'https://api.ukmeteors.co.uk/liveimages/getlive'
    try:
        liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')
        if len(liveimgs) > 0:
            assert True
        else:
            dtstr = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y%m%d') + '_01'
            liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')
            assert len(liveimgs) > 0
    except Exception as e: 
        print("failed with:" + repr(e))
        assert False


def test_getFireballFiles():
    patt = 'UK0006_20230421_2122'
    apiurl = 'https://api.ukmeteors.co.uk/fireballfiles'
    try:
        url = f'{apiurl}?pattern={patt}'
        print(url)
        fbfiles = pd.read_json(url)
        print(fbfiles)
        assert True
    except Exception as e:
        print("failed with:" + repr(e))
        assert False


def test_getDetections():
    srchapi = 'https://api.ukmeteors.co.uk/detections?'
    dt = datetime.datetime(2023,8,14,0,30,0)
    dt1 = (dt + datetime.timedelta(seconds=-30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    dt2 = (dt + datetime.timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    apiurl = f'{srchapi}d1={dt1}&d2={dt2}&opts=t:S'
    res = requests.get(apiurl)
    assert res.status_code == 200
    try:
        rawdata=res.text.strip()
        rawdata = rawdata[8:-2]
        _ = rawdata.split('"')
        assert True
    except Exception as e:
        print(repr(e))
        assert False


def test_getECSV():
    stationID = 'UK009C'
    dateStr = '2024-02-25T20:02:06.9'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == '593.580'

    stationID = 'UK009C'
    dateStr = '2024-02-25T20:02:06.978'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == '593.580'

    stationID = 'UK009C'
    dateStr = '20240225_200206_978'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == '593.580'

    stationID = 'UK009C'
    dateStr = '20240225_200206_977'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == 'time'

    stationID = 'UK0080'
    dateStr = '2024-02-25T20:02:00.1'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == '351.420'
    return 


def test_getECSVbadDate():
    stationID = 'UK0080'
    dateStr = '2024-02-25T20:02:'
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    assert res.text.split()[-1] == 'format'
    return 
