#
# nightly job metrics
#
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import os
import pandas as pd


def getVolStats(logf):
    with open(logf,'r') as inf:
        loglines = inf.readlines()
    
    logf = os.path.basename(logf)

    startcount = False
    stats=[]
    statid=''
    for li in loglines:
        li = li.strip()
        if 'Processing station:' in li and startcount is True:
            # no events from previous station
            #stats.append({'station':statid, 'events': 0})
            statid = li.split(' ')[2]
            startcount = True

        if 'Processing station:' in li and startcount is False:
            # new station to consider
            statid = li.split(' ')[2]
            startcount = True

        if 'Added' in li and 'observations' in li:
            # we got some data
            events = int(li.strip().split(' ')[1])
            if events > 0:
                stats.append({'station':statid, 'events': events})
            startcount = False

    df = pd.DataFrame(stats)
    df = df.sort_values(by=['events'], ascending=False)
    print(df[df.events > 500])
    print(sum(df.events))
    return df


if __name__ == '__main__':
    getVolStats(sys.argv[1])
