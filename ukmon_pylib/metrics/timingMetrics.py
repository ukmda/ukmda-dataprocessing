#
# nightly job metrics
#
import sys
import os
import datetime
import matplotlib.pyplot as plt


njstrs = ['nightlyJob: looking for matching',
    'nightlyJob: starting',
    "nightlyJob: getting list of single jpg files"
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


def graphOfData(logf, typ):
    if typ == 'M':
        with open(logf,'r') as inf:
            loglines = inf.readlines()
        times = []
        events = []
        elapsed = []
        cumul = 0
        daystart=0
        for li in loglines:
            spls = li.split(',')
            dtstamp = datetime.datetime.strptime(spls[0]+'_'+spls[1], '%Y%m%d_%H:%M:%S')
            times.append(dtstamp)
            events.append(spls[2].strip())
            if 'nightlyJob: starting' in li:
                print('resetting at ', dtstamp)
                cumul = 0
                daystart = dtstamp
            evttime = (dtstamp - daystart).seconds
            elapsed.append(evttime)
        #fig, ax = plt.subplots()
        l = len(times)
        t1 = times[l-16:]
        e1 = elapsed[l-16:]
        print(t1, e1)
        plt.plot(t1, e1)    
        plt.show()    
        plt.savefig('./timings.jpg')
        #return times, events, elapsed 



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
