#
# nightly job metrics
#
# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import glob
import datetime


def graphOfData(logf, dtstr):
    
    lis = open(logf,'r').readlines()
    dta = [li for li in lis if li[:8]==dtstr]

    # note: timings in log are the start times of the process
    # so we offset the labels by 1 to align with the end times
    times = []
    events = []
    elapsed = []
    lasttime = None
    starttime = None
    for li in dta:
        spls = li.split(',')
        currtime = datetime.datetime.strptime(f'{spls[0]}_{spls[1]}', '%Y%m%d_%H:%M:%S')
        if starttime is None:
            starttime = currtime
            lasttime = currtime
        elap = (currtime - starttime).seconds
        elapsed.append(elap)        # runtime so far
        events.append(spls[4].strip())      # event name
        times.append((currtime - lasttime).seconds) # duration of event
        lasttime = currtime
    
    fig, ax = plt.subplots()
    width = 0.35       
    ax.set_ylabel('Task')
    ax.set_xlabel('Duration (s)')
    ax.set_title('Batch Phases: {}'.format(dtstr))
    ax.barh(events, times, width)
    fig = plt.gcf()
    fig.set_size_inches(12, 12)
    fig.tight_layout()
    plt.xlim([0,5000])
    plt.grid(axis='x')
    plt.gca().invert_yaxis()
    logname, _ = os.path.splitext(os.path.basename(logf))
    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    os.makedirs(os.path.join(datadir, 'batchcharts'), exist_ok=True)
    plt.savefig(os.path.join(datadir, 'batchcharts',f'./{dtstr}-{logname}.jpg'), dpi=100)
    plt.close()



def getLogStats(nightlogf, matchlogf, thisdy):
    # logline example
    # <13>May  8 06:10:02 nightlyJob: start nightlyJob
    outdir = os.path.split(nightlogf)[0]
    
    loglines = open(nightlogf,'r').readlines()
    bsfs = [x for x in loglines if 'start'in x or 'finish' in x or 'end' in x]
    bsfs = [x for x in bsfs if x[0]=='<']

    loglines = open(matchlogf,'r').readlines()
    msfs = [x for x in loglines if 'start'in x or 'finish' in x or 'end' in x]
    msfs = [x for x in msfs if x[0]=='<']

    alldata = msfs + bsfs
    alldata.sort()
    starttime = None
    yr = datetime.datetime.now().year
    with open(os.path.join(outdir, 'perfNightly.csv'), 'a+') as outf:
        for rw in alldata:
            dtpart = rw[4:19]
            evtdt = datetime.datetime.strptime(f'{yr} {dtpart}', '%Y %b %d %H:%M:%S')
            if 'nightlyJob: starting' in rw:
                starttime = evtdt
            elapsed_secs = (evtdt - starttime).seconds
            txtpart = rw[20:]
            task = txtpart[:txtpart.find(':')]
            msg = txtpart[txtpart.find(':')+1:].replace(',', ' ')
            outstr = f'{evtdt.strftime("%Y%m%d,%H:%M:%S")},{elapsed_secs},{task},{msg}'
            outf.write(outstr)        
  

if __name__ == '__main__':
    dtstr = sys.argv[1]
    logdir = os.path.join(os.getenv('SRC',default=os.path.expanduser('~/prod')), 'logs')
    nowdt = datetime.datetime.now().strftime('%Y%m%d')
    if nowdt == dtstr:
        nightf = os.path.join(logdir, 'nightlyJob.log')
        matchf = os.path.join(logdir, 'matchJob.log')
    else:
        logs = glob.glob(os.path.join(logdir, f'*{dtstr}*.log'))
        nightf = None
        matchf = None
        for fn in logs:
            if 'matches' in fn:
                matchf = fn
            if 'nightlyJob' in fn:
                nightf = fn
    if nightf is None or matchf is None or not os.path.isfile(nightf) or not os.path.isfile(matchf):
        print('logfile missing')
        print(nightf, matchf)
    else:        
        getLogStats(nightf, matchf, dtstr)
        graphOfData('perfNightly.csv', dtstr)
