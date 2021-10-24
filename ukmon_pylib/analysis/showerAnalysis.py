#
# Python code to analyse meteor shower data
#

import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import datetime

from utils import getShowerDates as sd

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12


def getStatistics(sngldta, matchdta, outdir):
    numcams = len(sngldta.groupby('ID').size())
    numsngl = len(sngldta)
    nummatch = len(matchdta)
    matchgrps = matchdta.groupby('_Nos').size()
    nummatched = 0
    for index,row in matchgrps.items():
        nummatched += index * row
    return numcams, numsngl, nummatch, nummatched


def stationGraph(dta, shwrname, outdir, maxStats=20):
    print('creating count by station')
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    grps=dta.groupby('ID').size()
    ax=grps.sort_values(ascending=False).plot.bar()
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    fname = os.path.join(outdir, 'streamcounts_plot_by_station.jpg')
    plt.title('Count of single observations by station ({})'.format(shwrname))
    plt.savefig(fname)
    return len(grps)


def timeGraph(dta, shwrname, outdir, binmins=10):
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
    countcol = dta['Shwr']
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

    fname = os.path.join(outdir, 'stream_plot_timeline_single.jpg')
    plt.title('Observed stream activity {}min intervals ({})'.format(binmins, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    return len(dta)


def matchesGraphs(dta, shwrname, outdir, binmins=60):
    print('Creating matches binned graph')
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    # add a datetime column so i can bin the data
    mdta = dta.assign(dt = pd.to_datetime(dta['_localtime'], format='_%Y%m%d_%H%M%S'))
    # set the datetime to be the index
    mdta = mdta.set_index('dt')
    #select just the shower ID col
    mcountcol = mdta['_ID1']
    # resample it 
    mbinned = mcountcol.resample('{}min'.format(binmins)).count()
    mbinned.plot(kind='bar')

    # set ticks and labels every 144 intervals
    plt.locator_params(axis='x', nbins=len(mbinned)/24)
    #plt.xticks(rotation=0)
    # set font size
    ax = plt.gca()
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)
        
    # format x-axes
    x_labels = mbinned.index.strftime('%b-%d')
    ax.set_xticklabels(x_labels)
    ax.set(xlabel="Date", ylabel="Count")

    fname = os.path.join(outdir, 'stream_plot_timeline_matches.jpg')
    plt.title('Confirmed stream activity {}min intervals ({})'.format(binmins, shwrname))
    plt.tight_layout()
    plt.savefig(fname)

    plt.clf()
    # set paper size so fonts look good
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)


    matchgrps = dta.groupby('_Nos').size()
    matchgrps.plot.barh()
    ax = plt.gca()
    ax.set(xlabel="Count", ylabel="# Stations")

    fname = os.path.join(outdir, 'stream_plot_by_correllation.jpg')
    plt.title('Number of Matched Observations ({})'.format(shwrname))
    plt.tight_layout()
    plt.savefig(fname)

    nummatched = 0
    for index,row in matchgrps.items():
        nummatched += index * row

    return len(dta), nummatched

def magDistributionAbs(dta, shwrname, outdir, binwidth=0.2):
    print('Creating matches abs mag histogram')
    plt.clf()

    magdf=pd.DataFrame(dta['_mag'])
    bins=np.arange(-6,6+binwidth,binwidth)
    magdf['bins']=pd.cut(magdf['_mag'], bins=bins, labels=bins[:-1])

    gd1 = magdf.groupby(magdf.bins).count().plot(kind='bar')
    ax = plt.gca()
    ax.set(xlabel="Magnitude", ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    x_labels=["%.0f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)
    print(plt.gcf())  

    fname = os.path.join(outdir, 'stream_plot_mag.jpg')
    plt.title('Abs Magnitude Distribution in bins of width {} ({})'.format(binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    return 


def magDistributionVis(dta, shwrname, outdir, binwidth=0.2):
    print('Creating detections visual mag histogram')

    magdf=pd.DataFrame(dta['Mag'])
    bins=np.arange(-6,6+binwidth,binwidth)
    magdf['bins']=pd.cut(magdf['Mag'], bins=bins, labels=bins[:-1])

    gd = magdf.groupby(magdf.bins).count()
    gd.plot(kind='bar')
    ax = plt.gca()
    ax.set(xlabel="Magnitude", ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)
        
    # format x-axes
    x_labels=["%.0f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, 'stream_plot_vis_mag.jpg')
    plt.title('Visual Magnitude Distribution in bins of width {} ({})'.format(binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    return 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python showerAnalysis.py GEM 2017')
        exit(0)
    yr=int(sys.argv[2])
    shwr = sys.argv[1]

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    # set up paths, files etc
    outdir = os.path.join(datadir, 'reports', str(yr), shwr)
    os.makedirs(outdir, exist_ok=True)

    singleFile = os.path.join(datadir, 'single', 'singles-{}.csv'.format(yr))
    matchfile = os.path.join(datadir, 'matched', 'matches-{}.csv'.format(yr))

    # read the data
    sngl = pd.read_csv(singleFile)
    mtch = pd.read_csv(matchfile, skipinitialspace=True)

    # select the required data
    if shwr != 'ALL':
        id, shwrname, sl, dt = sd.getShowerDets(sys.argv[1])
        shwrfltr = sngl[sngl['Shwr']==shwr]
        mtchfltr = mtch[mtch['_stream']==shwr]
    else:
        shwrname = 'All Showers'
        shwrfltr = sngl
        mtchfltr = mtch

    numsngl = 0
    numcams = 0
    nummatch = 0
    nummatched = 0
    # now get the graphs and stats
    if len(shwrfltr) > 0:
        numsngl = timeGraph(shwrfltr, shwrname, outdir, 10)
        numcams = stationGraph(shwrfltr, shwrname, outdir, 20)
        magDistributionVis(shwrfltr, shwrname, outdir)
    if len(mtchfltr) > 0:
        nummatch, nummatched = matchesGraphs(mtchfltr, shwrname, outdir, 60)
        magDistributionAbs(mtchfltr, shwrname, outdir)
    
    print(numcams, numsngl, nummatch, nummatched)
