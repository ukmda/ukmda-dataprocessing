#
# Copyright (C) 2018-2023 Mark McIntyre

import datetime
import json
import requests 
import pandas as pd


def test_matchApiCall():
    reqtyp = 'matches'
    reqval = '20230721'
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}'
    matchlist = pd.read_json(apicall, lines=True)   
    assert len(matchlist) != 339
    assert matchlist.orbname[0] == '20230721_000106.311_UK'


def test_getMatchPickle():
    patt = '20220814_205940.252_UK'
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
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
    dtstr = datetime.datetime.now().strftime('%Y%m%d') + '_0100'
    apiurl = 'https://api.ukmeteornetwork.co.uk/liveimages/getlive'
    try:
        liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')    
        assert len(liveimgs) > 0
    except Exception as e: 
        print("failed with:" + repr(e))
        assert False


def test_fetchECSV():
    stationID = 'UK0006'
    dateStr = '2023-08-31T01:28:57.41'
    apiurl='https://api.ukmeteornetwork.co.uk/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stationID, dateStr))
    assert res.status_code == 200
    return 
    

def test_getFireballFiles():
    patt = 'UK0006_20230421_2122'
    apiurl = 'https://api.ukmeteornetwork.co.uk/fireballfiles'
    try:
        url = f'{apiurl}?pattern={patt}'
        print(url)
        fbfiles = pd.read_json(url)
        print(fbfiles)
        assert True
    except Exception as e:
        print("failed with:" + repr(e))
        assert False


def detailApiCall1(reqtyp, reqval):
    """ get details of one matched event """
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}'
    evtdetail = pd.read_json(apicall, typ='series')
    return evtdetail


def detailApiCall2(reqtyp, matchlist):
    """
    get details for the events in the match list for a given date
    and put them in a pandas dataframe, then sort by brightest
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    details = []
    for id in matchlist.head(5).orbname:
        reqval = id
        apicall = f'{apiurl}?reqtyp={reqtyp}&reqval={reqval}'
        details.append(pd.read_json(apicall, typ='series'))
    df = pd.DataFrame(details)
    df = df.sort_values(by=['_mag'])
    return df
