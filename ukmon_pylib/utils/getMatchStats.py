#
# python to get matching engine statistics
#

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

    trajs = [line.strip() for line in loglines if 'SOLVING' in line and 'TRAJECTORIES' in line]
    spls = trajs[0].split(' ')
    trajs = int(spls[1])

    nonphys = beglowr + badalti + badvelo + badangl 
    tot = added + uncal + missdf
    return tot, added, uncal, missdf, nonphys, trajs


if __name__ == '__main__':
    tot, added, uncal, missdf, nonphys, trajs = getMatchStats(sys.argv[1])
    print(tot, added, uncal, missdf, nonphys, trajs)
