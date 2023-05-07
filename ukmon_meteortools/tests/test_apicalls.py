from usertools.apiExampleCode import matchApiCall, detailApiCall1, detailApiCall2
from usertools.apiExampleCode import trajectoryAPI, getLiveimageList, getFireballFiles, getMatchPickle


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


def test_trajectoryAPI():
    traj = '20230213_025913.678_UK'
    retval = trajectoryAPI(traj)
    assert retval is not None


def test_getMatchPickle():
    patt = '20230501_002536.754_UK'
    pf = getMatchPickle(patt)
    assert pf['file_name'] == '20230501_002536'


def test_getLiveImages():
    dtstr = '20230506_0250'
    lst = getLiveimageList(dtstr)
    assert len(lst) == 3


def test_getFireballFiles():
    patt = 'UK0006_20230421_2122'
    fblist = getFireballFiles(patt)
    assert len(fblist) > 0
