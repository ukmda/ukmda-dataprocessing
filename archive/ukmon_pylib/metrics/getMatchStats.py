# Copyright (C) 2018-2023 Mark McIntyre
#
# python to get matching engine statistics
#

from datetime import datetime
import sys


def getDailyObsCounts(logf):
    loglines = open(logf).readlines()
    addlines = [line.strip() for line in loglines if ('Added' in line and 'observations' in line) or 'Processing station' in line]
    res=[0,0,0,0]
    stn = ''
    offs = 0
    totalval = 0
    uniquestns = 0
    for i in range(len(addlines)):
        if 'Processing' in addlines[i]:
            print(addlines[i])
            newstn = addlines[i].split(' ')[-1]
            if stn != newstn:
                stn = newstn
                offs = 0
                uniquestns += 1
            if 'Processing' in addlines[i+1]:
                continue
            val = int(addlines[i+1].split(' ')[1])
            totalval += val
            res[offs] += val
            offs += 1
    print(res, uniquestns)
    return


def getMatchStats(logf):
    loglines = open(logf).readlines()

    events = [line.strip() for line in loglines if 'Analysing' in line and 'observations' in line]
    if len(events) > 0: 
        # new-style log
        addlines = [x for x in events if '0 observations' not in x]
        addoffs = -5
        oldstyle = False
    else:
        addlines = [line.strip() for line in loglines if 'Added' in line and 'observations' in line]
        addoffs = 1
        oldstyle = True
    
    uncal = len([line.strip() for line in loglines if 'Skipping' in line and 'recalibrated' in line])
    missdf = len([line.strip() for line in loglines if 'Skipping' in line and 'missing data' in line])

    added=0
    for li in addlines:
        spls=li.split(' ')
        added += int(spls[addoffs])
    
    beglowr = len([line.strip() for line in loglines if 'Begin height lower than the end height' in line])
    badalti = len([line.strip() for line in loglines if 'Meteor heights outside allowed range' in line])
    badvelo = len([line.strip() for line in loglines if 'Velocity difference too high' in line])
    badangl = len([line.strip() for line in loglines if 'Max convergence angle too small' in line])

    if oldstyle:
        trajs = [line.strip() for line in loglines if 'SAVING' in line and 'CANDIDATES' in line]
        spls = trajs[0].split(' ')
        trajs = int(spls[1])
    else:
        trajs = 0
        trajlines = [line.strip() for line in loglines if 'Saved' in line and '0 candidates' not in line]
        for li in trajlines:
            spls=li.split(' ')
            trajs += int(spls[-2])

    nonphys = beglowr + badalti + badvelo + badangl 
    tot = added + uncal + missdf

    rtims = [line.strip() for line in loglines if 'runDistrib' in line]
    stim = rtims[0][11:19]
    etim = rtims[-1][11:19]
    d1=datetime.strptime(stim,'%H:%M:%S')
    d2=datetime.strptime(etim,'%H:%M:%S')
    runtime = str(d2 - d1)

    cstims = [line.strip() for line in loglines if 'execdistrib' in line]
    stim = cstims[0][11:19]
    etim = cstims[-1][11:19]
    d1=datetime.strptime(stim,'%H:%M:%S')
    d2=datetime.strptime(etim,'%H:%M:%S')
    cstime = str(d2 - d1)

    return tot, added, uncal, missdf, nonphys, trajs, runtime, cstime


if __name__ == '__main__':
    tot, added, uncal, missdf, nonphys, trajs, runtime, cstime = getMatchStats(sys.argv[1])
    print(tot, added, uncal, missdf, nonphys, trajs, runtime, cstime)
