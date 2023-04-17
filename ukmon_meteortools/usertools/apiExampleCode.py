#
# Example showing how to use the matchdata API from Python
#
# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd

apiurl = 'https://api.ukmeteornetwork.co.uk/matches'


def matchApiCall(reqtyp, reqval):
    # get names of all matches for a given date
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    matchlist = pd.read_json(apicall, lines=True)
    return matchlist


def detailApiCall1(reqtyp, reqval):
    # get details of one event
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    evtdetail = pd.read_json(apicall, typ='series')
    return evtdetail


def detailApiCall2(reqtyp, matchlist):
    # get details for the first five events in the match list
    # and put them in a pandas dataframe, then sort by brightest
    details = []
    for id in matchlist.head(5).orbname:
        reqval = id
        apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
        details.append(pd.read_json(apicall, typ='series'))
    df = pd.DataFrame(details)
    df = df.sort_values(by=['_mag'])
    return df


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
