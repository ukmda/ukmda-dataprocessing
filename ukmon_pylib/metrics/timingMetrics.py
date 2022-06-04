#
# nightly job metrics
#
import sys
import os
import datetime
import matplotlib.pyplot as plt


njstrs = ['nightlyJob: looking for matching',
    'nightlyJob: starting',
    'nightlyJob: forcing consolidation of',
    'nightlyJob: Create density',
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
    'nightlyJob: Finished',
    'stationReports: finished',
    'stationReports: running station reports']

mlstrs=[
    'findAllMatches: load the WMPL',
    'findAllMatches: get all UFO data',
    'convertUfoToRms: finished',
    'runDistrib: deploy the script to the server',
    'runDistrib: starting correlator',
    'runDistrib: done and syncing back',
    'runDistrib: finished',
    'findAllMatches: create text file containing',
    'findAllMatches: update the website loop',
    'findAllMatches: gather some stats',
    'findAllMatches: Matching process finished'
]


def graphOfData(logf, typ):
    if typ == 'M':
        with open(logf,'r') as inf:
            loglines = inf.readlines()
        times = []
        events = []
        elapsed = []
        daystart=0
        for li in loglines:
            spls = li.split(',')
            dtstamp = datetime.datetime.strptime(spls[0]+'_'+spls[1], '%Y%m%d_%H:%M:%S')
            times.append(dtstamp)
            events.append(spls[2].strip())
            if 'nightlyJob: starting' in li:
                print('resetting at ', dtstamp)
                daystart = dtstamp
            evttime = (dtstamp - daystart).seconds
            elapsed.append(evttime)
        #fig, ax = plt.subplots()
        le = len(times)
        t1 = times[le - 16:]
        e1 = elapsed[le - 16:]
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
