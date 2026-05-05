# Copyright (C) 2018-2023 Mark McIntyre
#
# python to get matching engine statistics
#

from datetime import datetime
import sys
import os
import glob
from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase


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


def getMatchStats(logf, rundate):
    loglines = open(logf).readlines()

    events = [line.strip() for line in loglines if 'Analysing' in line and 'observations' in line]
    if len(events) > 0: 
        # new-style log
        addlines = [x for x in events if ' 0 observations' not in x]
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

    cands = 0
    if oldstyle:
        cands = [line.strip() for line in loglines if 'SAVING' in line and 'CANDIDATES' in line]
        spls = cands[0].split(' ')
        cands = int(spls[1])
    else:
        trajlines = [line.strip() for line in loglines if 'Saved' in line and ' 0 candidates' not in line]
        for li in trajlines:
            spls=li.split(' ')
            cands += int(spls[-2])

    nonphys = beglowr + badalti + badvelo + badangl 
    tot = added + uncal + missdf

    rtims = [line.strip() for line in loglines if 'runDistrib' in line and '/prod/' not in line]
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

    datadir=os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    dailydbdir = os.path.join(datadir, 'latest','dailydbs')
    trajdb = TrajectoryDatabase(dailydbdir, f'{rundate}_trajectories.db')
    trajs = len(trajdb.getTrajBasics('.',[0,9999999]))

    return tot, added, uncal, missdf, nonphys, cands, trajs, runtime, cstime


def updateStats(obscount, candcount, trajcount, runtime, rundate):
    datadir=os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    statsdir = os.path.join(datadir, 'dailyreports')
    reports = glob.glob(os.path.join(statsdir, f'{rundate}*.txt'))

    # only update stats if the daily report exists already
    if len(reports) > 0:
        dailyrep = os.path.split(reports[-1])[1]
        statsdata = open(os.path.join(statsdir,'stats.txt'), 'r').readlines()

        # remove any existing entry for today
        currentstats = [li for li in statsdata if rundate in li]
        if len(currentstats) > 0:
            statsdata.pop(statsdata.index(currentstats[0]))
        # add the new entry and save
        statsdata.append(f'{dailyrep} {obscount} {candcount} {trajcount} {runtime}\n')
        open(os.path.join(statsdir,'stats.txt'), 'w').writelines(statsdata)
    return 


if __name__ == '__main__':
    matchfile = sys.argv[1]
    rundate = sys.argv[2]

    tot, added, uncal, missdf, nonphys, cands, trajs, runtime, cstime = getMatchStats(matchfile, rundate)

    updateStats(added, cands, trajs, runtime, rundate)
    print(tot, added, uncal, missdf, nonphys, cands, trajs, runtime, cstime)
