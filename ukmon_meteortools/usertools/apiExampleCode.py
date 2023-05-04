#
# Example showing how to use the matchdata API from Python
#
# Copyright (C) 2018-2023 Mark McIntyre

"""
Examples showing how to use the APIs. 
"""

import pandas as pd


def matchApiCall(reqtyp, reqval):
    """get names of all matches for a given date"""
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    matchlist = pd.read_json(apicall, lines=True)
    return matchlist


def getMatchPickle(patt):
    """
    get the pickled trajectory for a given matched event   
    Returns a json object containing the pickled data
    
    Example pattern 20230501_002536.754_UK
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    apicall = f'{apiurl}?reqval={patt}'
    matchpickle = pd.read_json(apicall, lines=True)
    return matchpickle


def detailApiCall1(reqtyp, reqval):
    """ get details of one event """
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    evtdetail = pd.read_json(apicall, typ='series')
    return evtdetail


def detailApiCall2(reqtyp, matchlist):
    """
    get details for the first five events in the match list 
    and put them in a pandas dataframe, then sort by brightest
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/matches'
    details = []
    for id in matchlist.head(5).orbname:
        reqval = id
        apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
        details.append(pd.read_json(apicall, typ='series'))
    df = pd.DataFrame(details)
    df = df.sort_values(by=['_mag'])
    return df


def getLiveimageList(dtstr):
    """ 
    Get a list of livestream images matching a pattern YYYYMMDD_HHMMSS.  
    The seconds and minutes parts are optional but huge amounts of data may get returned.  

    Example pattern: '20230421_2122'
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/liveimages/getlive'
    liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')
    return liveimgs


def getFireballFiles(patt):
    """ 
    Get a zip file containing the fireball data matching a pattern of the form UKxxxx_YYYYMMDD_HHMMSS
    Nothing will be returned if there is no fireball data available. 

    Example pattern: 'UK0006_20230421_2122'

    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/fireballs/getfb'
    fbfiles = pd.read_json(f'{apiurl}?pattern={patt}')
    return fbfiles


if __name__ == '__main__':
    # get all matched events for a given date
    reqtyp = 'matches'
    reqval = '20211121'
    matchlist = matchApiCall(reqtyp, reqval)
    print(matchlist)

    reqtyp = 'detail'
    reqval = '20211121_032219.699_UK'
    evtlist = detailApiCall1(reqtyp, reqval)
    print(evtlist)

    reqtyp = 'detail'
    evt = detailApiCall2(reqtyp, matchlist)
    print(evt)
