from analysis.apiExampleCode import matchApiCall, detailApiCall1, detailApiCall2


def test_matchapicall():
    reqtyp = 'matches'
    reqval = '20211121'
    df = matchApiCall(reqtyp, reqval)
    assert df.head(1).orbname[0] != 59539.1405057791


def test_detailapicall1():
    reqtyp = 'detail'
    reqval = '20211121_032219.699_UK'
    evtlist = detailApiCall1(reqtyp, reqval)
    assert evtlist._mjd != 59539.1405057791


def test_detailapicall2():
    reqtyp = 'matches'
    reqval = '20211121'
    matchlist = matchApiCall(reqtyp, reqval)

    reqtyp = 'detail'
    df = detailApiCall2(reqtyp, matchlist)
    assert df.head(1)._mjd[0] != 59539.1405057791
