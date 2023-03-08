#
# simple code to analyse GMN data
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def loadOneMonth(dtstr):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    gmndir = os.path.join(datadir, '..', 'gmndata')
    srcfile = os.path.join(gmndir, f'traj_summary_monthly_{dtstr}.txt')
    df = pd.read_csv(srcfile, header=1, skiprows=1, sep=';', skipinitialspace=True)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    ukdf = df[df.stations.str.contains('UK')]
    stnlist =  ','.join(list(ukdf.stations)).split(',')
    stns = list(dict.fromkeys(stnlist))
    ukstns = [v for v in stns if 'UK' in v]
    
    return ukstns, ukdf


def getAnnualData(yrstr):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    gmndir = os.path.join(datadir, '..', 'gmndata')
    mth=[]
    stncount=[]
    matchcount=[]
    maxcams=[]
    moreten=[]
    allmatches=[]
    fulldf = pd.DataFrame()
    for i  in range(1,13):
        dtstr = f'{yrstr}{i:02d}'
        stns, matches, allm = loadOneMonth(dtstr)
        fulldf = pd.concat([fulldf, matches])
        mth.append(dtstr)
        allmatches.append(allm)
        stncount.append(len(stns))
        matchcount.append(len(matches))
        maxcams.append(max(matches.stat.astype(int)))
        moreten.append(len(matches[matches.stat.astype(int) > 9])) 
    with open(os.path.join(gmndir, f'summary-{yrstr}.csv'), 'w') as outf:
        for d, s, c, mc, m10 in zip(mth, stncount, matchcount, maxcams, moreten):
            outf.write(f'{d},{s},{c},{mc},{m10}\n')
    print(max(stncount), sum(matchcount), max(maxcams), sum(moreten), sum(allmatches))
    return mth, stncount, matchcount, maxcams, moreten, fulldf


def matchesGraph(mth, matchcount):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    gmndir = os.path.join(datadir, '..', 'gmndata')
    outfname = os.path.join(gmndir, f'matches-{mth[0][:4]}.jpg')
    plt.clf()
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fig = plt.figure()
    fig.set_size_inches(11.6, 8.26)    
    ax = fig.add_axes([0,0,1,1])
    ax.bar(mth, matchcount, color='b')
    ax.set_title('2022 Matches by Month - UK')
    ax.set_xlabel('Month')
    ax.set_ylabel('# Matches')
    #plt.tight_layout()
    plt.savefig(outfname)
    plt.show()
    plt.close()
    return 


if __name__ == '__main__':
    yrstr = sys.argv[1]
    mth, stncount, matchcount, maxcams, moreten, fulldf = getAnnualData(yrstr)
