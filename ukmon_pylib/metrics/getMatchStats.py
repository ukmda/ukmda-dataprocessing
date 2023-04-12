# Copyright (C) 2018-2023 Mark McIntyre
#
# python to get matching engine statistics
#

from datetime import datetime
import sys


def getMatchStats(logf):
    with open(logf) as inf:
        loglines = inf.readlines()
    
    addlines = [line.strip() for line in loglines if 'Added' in line and 'observations' in line]
    nocallines = [line.strip() for line in loglines if 'Skipping' in line and 'recalibrated' in line]
    misdflines = [line.strip() for line in loglines if 'Skipping' in line and 'missing data' in line]
    uncal = len(nocallines)
    missdf = len(misdflines)
    added=0
    for li in addlines:
        spls=li.split(' ')
        added = added + int(spls[1])
    
    beglowr = len([line.strip() for line in loglines if 'Begin height lower than the end height' in line])
    badalti = len([line.strip() for line in loglines if 'Meteor heights outside allowed range' in line])
    badvelo = len([line.strip() for line in loglines if 'Velocity difference too high' in line])
    badangl = len([line.strip() for line in loglines if 'Max convergence angle too small' in line])

    trajs = [line.strip() for line in loglines if 'SAVING' in line and 'CANDIDATES' in line]
    spls = trajs[0].split(' ')
    trajs = int(spls[1])

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
