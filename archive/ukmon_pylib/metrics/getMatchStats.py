# Copyright (C) 2018-2023 Mark McIntyre
#
# python to get matching engine statistics
#

import datetime
import sys
import os
import glob
import tarfile

from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase

from analysis.getUsedUnused import getObservationCount


def getDailyObsCount(startdt, rundate):
    """
    Get a count of all observations in the period defined by startdt to rundate

    Arguments:
    startdt:    [string] start-date in the format YYYYMMDD-HHMMSS
    rundate:    [string] end-date in the foramt YYYYMMDD 

    returns:
    count of candidates within that window

    """

    sdt = datetime.datetime.strptime(startdt, '%Y%m%d-%H%M%S')
    edt = datetime.datetime.strptime(f'{rundate}-080000', '%Y%m%d-%H%M%S')
    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    dbdir = os.path.join(datadir,'distrib')
    return getObservationCount([sdt, edt], dbdir)


def getDailyCandCount(rundate):
    """ 
    Obtain a count of candidates for a given date

    Arguments
    rundate: [str] date to run for in YYYYMMDD format

    """
    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    cand_tgz = os.path.join(datadir, 'distrib','candidates',f'{rundate}.tgz')
    if os.path.isfile(cand_tgz):
        try:
            return len(tarfile.open(cand_tgz,'r:gz').getnames())
        except Exception as e:
            print(f'unable to read candidate tarfile {cand_tgz}')
            print(e)
            return 0
    else:
        return 0
    

def getDailyTrajCount(rundate):
    """ 
    Obtain a count of trajectories for a given date

    Arguments
    rundate: [str] date to run for in YYYYMMDD format

    """
    datadir=os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    dailydbdir = os.path.join(datadir, 'latest','dailydbs')
    if os.path.isfile(os.path.join(dailydbdir, f'{rundate}_trajectories.db')):
        trajdb = TrajectoryDatabase(dailydbdir, f'{rundate}_trajectories.db')
        return len(trajdb.getTrajBasics('.',[0,9999999]))
    else:
        return 0


def getRunTime(rundate, totalruntime=True):
    """
    Gets the runtime for runDistrib or execdistrib
    Arguments:
    rundate: [str] date to run for in YYYYMMDD format

    keyword arguments:
    totalruntime: [bool] if true, return the total runtime for runDistrib. 
                         Otherwise return the runtime for candidate finding, distribution and solving

    returns:
        runtime: [timedelta] a datetime.timedelta representation of the runtime
    """

    cmd = f'journalctl -t runDistrib -S "{rundate[:4]}-{rundate[4:6]}-{rundate[6:8]}T00:00:00Z"'
    loglines = os.popen(cmd).read().split('\n')

    starttime = None
    finishtime = None
    if totalruntime:
        finishline = None
        startedlines = [x for x in loglines if 'running phase 1' in x and f'to {rundate}' in x]
        for i in reversed(range(len(startedlines))):
            startline = startedlines[i]
            starttime = startedlines[i].split(' ')[2]
            starttime = datetime.datetime.strptime(f'{rundate} {starttime}', '%Y%m%d %H:%M:%S')
            currline = loglines.index(startline)
            for j in range(currline, len(loglines)):
                if 'finished' in loglines[j] and 'consolidation' not in loglines[j]:
                    finishline = loglines[j]
                    finishtime = finishline.split(' ')[2]
                    finishtime = datetime.datetime.strptime(f'{rundate} {finishtime}', '%Y%m%d %H:%M:%S')
                    break
            if finishtime:
                break
        if starttime and finishtime:
            return (finishtime -starttime)
        else:
            print('unable to get runtime')
            return datetime.timedelta(0)
    else:
        finishedlines = [x for x in loglines if f'finished consolidation for {rundate}' in x]
        finishtime = finishedlines[-1].split(' ')[2]
        finishtime = datetime.datetime.strptime(f'{rundate} {finishtime}', '%Y%m%d %H:%M:%S')

        startedlines = [x for x in loglines if f'start distributed processing for {rundate}' in x]
        starttime = None
        for i in reversed(range(len(startedlines))):
            starttime = startedlines[i].split(' ')[2]
            starttime = datetime.datetime.strptime(f'{rundate} {starttime}', '%Y%m%d %H:%M:%S')
            if starttime < finishtime:
                break
        if starttime:
            return (finishtime -starttime)
        else:
            print('unable to get runtime')
            return datetime.timedelta(0)


def getMatchStats(logf, rundate, startdt):
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

    nonphys = beglowr + badalti + badvelo + badangl 
    tot = added + uncal + missdf

    obs = getDailyObsCount(startdt, rundate)
    cands = getDailyCandCount(rundate)
    trajs = getDailyTrajCount(rundate)
    runtime = str(getRunTime(rundate))
    cstime = str(getRunTime(rundate, totalruntime=False))

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
    startdt = sys.argv[3]

    tot, added, uncal, missdf, nonphys, cands, trajs, runtime, cstime = getMatchStats(matchfile, rundate, startdt)

    updateStats(added, cands, trajs, runtime, rundate)
    print(tot, added, uncal, missdf, nonphys, cands, trajs, runtime, cstime)
