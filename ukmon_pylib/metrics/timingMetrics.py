#
# nightly job metrics
#
import sys
import os


njstrs = ['nightlyJob: looking for matching',
    'nightlyJob: update shower associations',
    'createMthlyExtracts: starting',
    'createMthlyExtracts: finished',
    'createShwrExtracts: starting',
    'createShwrExtracts: finished',
    'nightlyJob: update search index',
    'updateSearchIndex: finished',
    'monthlyReports: getting latest combined files',
    'monthlyReports: Getting single detections',
    'monthlyReports: running ALL report for 2021',
    'nightlyJob: update other relevant showers',
    'nightlyJob: create the cover page',
    'nightlyJob: Finished']

mlstrs=[
    'findAllMatches: load the WMPL',
    'findAllMatches: get all UFO data',
    'convertUfoToRms: finished',
    'runMatching: deploy the script to the server',
    'runMatching: starting correlator',
    'runMatching: done and syncing back',
    'runMatching: finished',
    'findAllMatches: create text file containing',
    'findAllMatches: update the website loop',
#    'createPageIndex: generate extra data files',
#    'createPageIndex: generating orbit',
    'findAllMatches: gather some stats',
#    'createOrbitIndex: finished',
    'findAllMatches: Matching process finished'
]


def getLogStats(logf, typ):
    with open(logf,'r') as inf:
        loglines = inf.readlines()
    
    logf = os.path.basename(logf)
    spls = logf.split('-')
    thisdy= spls[1]
    if typ=='M':
        matchstrs = mlstrs
    else:
        matchstrs = njstrs

    for li in loglines:
        if any(msg in li for msg in matchstrs):
            ts = li[11:19]
            msg=li[20:].strip()
            print('{},{},{}'.format(thisdy, ts, msg))


if __name__ == '__main__':
    getLogStats(sys.argv[1],sys.argv[2])
