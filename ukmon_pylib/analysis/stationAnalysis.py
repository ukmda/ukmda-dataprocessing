#
# Python code to analyse meteor shower data
#

import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from wmpl.Utils.TrajConversions import jd2Date

from utils import getShowerDates as sd
from fileformats import CameraDetails as cd

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

def getBrightest(mtch, xtra, loc, outdir, when):
    brightest = mtch[mtch['_mjd'].isin (list(xtrafltr['mjd']))].nsmallest(10, ['_mag'])
    fbs=[]
    fname = os.path.join(outdir, 'station_brightest.csv')
    with open(fname, 'w') as outf:
        for r in brightest.iterrows():
            fbs.append({'mjd': r[1]._mjd, 'mag': r[1]._mag, 'shwr':r[1]._stream})
            dt = jd2Date(r[1]._mjd + 2400000.5, dt_obj=True)
            outf.write('{},{},{}\n'.format(dt.strftime('%Y%m%d_%H%M%S.%f'),r[1]._mag,r[1]._stream))
    return fbs

def timeGraph(dta, loc, outdir, when, binmins=10):
    print('Creating single station binned graph')
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    # add a datetime column so i can bin the data
    dta = dta.assign(dt = pd.to_datetime(dta['Dtstamp'], unit='s'))
    # set the datetime to be the index
    dta = dta.set_index('dt')
    #select just the shower ID col
    countcol = dta['ID']
    # resample it 
    binned = countcol.resample('{}min'.format(binmins)).count()
    binned.plot(kind='bar')

    # set ticks and labels every 144 intervals
    plt.locator_params(axis='x', nbins=len(binned)/144)
    #plt.xticks(rotation=0)
    # set font size
    ax = plt.gca()
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)
        
    # format x-axes
    x_labels = binned.index.strftime('%b-%d')
    ax.set_xticklabels(x_labels)
    ax.set(xlabel="Date", ylabel="Count")

    fname = os.path.join(outdir, 'station_plot_timeline_single.jpg')
    plt.title('Observed stream activity {}min intervals for {} in {}'.format(binmins, loc, when))
    plt.tight_layout()
    plt.savefig(fname)
    return len(dta)


def shwrGraph(dta, loc, outdir, when):
    print('Creating showers by station')
    plt.clf()

    dta.groupby('Shwr').count().sort_values(by='Ver', ascending=True).Ver.plot.barh()

    ax = plt.gca()
    ax.set(xlabel="Count", ylabel="Shower")
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, 'showers_by_station.jpg')
    plt.title('Showers observed by {} in {}'.format(loc, when))
    plt.tight_layout()
    plt.savefig(fname)

    return 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python stationAnalysis.py Tackley 201710')
        exit(0)
    ym=sys.argv[2]
    loc = sys.argv[1]
    yr = int(ym[:4])
    when = ym[:4]
    mth = None
    if len(ym) > 4:
        mth = int(ym[4:6])
        when = '{:02d}/{}'.format(mth, yr)

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    # set up paths, files etc
    if mth is None: 
        outdir = os.path.join(datadir, 'reports', str(yr), 'stations', loc)
    else:
        outdir = os.path.join(datadir, 'reports', str(yr), 'stations', loc, '{:02d}'.format(mth))
    os.makedirs(outdir, exist_ok=True)

    singleFile = os.path.join(datadir, 'single', 'singles-{}.csv'.format(yr))
    matchfile = os.path.join(datadir, 'matched', 'matches-{}.csv'.format(yr))
    extrafile = os.path.join(datadir, 'matched', 'matches-extras-{}.csv'.format(yr))

    # read the data
    sngl = pd.read_csv(singleFile)
    mtch = pd.read_csv(matchfile, skipinitialspace=True)
    xtra = pd.read_csv(extrafile, skipinitialspace=True)

    si = cd.SiteInfo('e:/dev/meteorhunting/ukmon-keymgmt/caminfo/camera-details.csv')
    idlist = si.getStationsAtSite(loc)
    # select the required data
    statfltr = sngl[sngl['ID'].isin( idlist)]
    xtrafltr = pd.DataFrame()
    for id in idlist:
        xtmp = xtra[xtra['stations'].str.contains(id)]    
        xtrafltr = xtrafltr.append(xtmp).drop_duplicates()
    
    if mth is not None:
        statfltr = statfltr[statfltr['M']==mth]
        xtrafltr = xtrafltr[xtrafltr['# date'].str[:6].isin([ym])]

    numsngl = len(statfltr)
    if numsngl > 0:
        timeGraph(statfltr, loc, outdir, when, 30)
        shwrGraph(statfltr, loc, outdir, when)
    nummatch = len(xtrafltr)
    if nummatch > 0:
        fbs = getBrightest(mtch, xtrafltr, loc, outdir, when)

    print(numsngl, nummatch)
