#
# Python code to analyse meteor shower data
#
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime

from ukmon_pytools.utils import getShowerDates as sd
from ukmon_pytools.fileformats import imoWorkingShowerList as imo

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12


def logMessage(msg):
    dtstr = datetime.datetime.now().strftime('%b %d %H:%M:%S')
    print(f'<13>{dtstr} {msg}')
    return


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
    logMessage('creating count by station')
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    grps=dta.groupby('ID').size()
    ax=grps.sort_values(ascending=False).plot.bar()
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    fname = os.path.join(outdir, '01_streamcounts_plot_by_station.jpg')
    plt.title('Count of single observations by station ({})'.format(shwrname))
    plt.savefig(fname)
    plt.close()
    return len(grps)


def showerGraph(dta, s_or_m, outdir, shwrname='ALL', maxshwrs=30):
    logMessage('creating {} count by shower'.format(s_or_m))
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    if s_or_m == 'observed':
        dta = dta[dta.Shwr !='spo']
        grps = dta.groupby('Shwr').size()
    else:
        dta = dta[dta._stream !='spo']
        grps = dta.groupby('_stream').size()
    if len(dta) > 0: 
        ax=grps.sort_values(ascending=False).head(maxshwrs).plot.barh()
        for lab in ax.get_xticklabels():
            lab.set_fontsize(SMALL_SIZE)

        fname = os.path.join(outdir, '01_streamcounts_plot_shower_{}.jpg'.format(s_or_m))
        plt.title('Top {} showers - {} events ({})'.format(maxshwrs, s_or_m, shwrname))
        plt.savefig(fname)
        plt.close()
    return len(grps)


def timeGraph(dta, shwrname, outdir, binmins=10):
    logMessage('Creating single station binned graph')
    fname = os.path.join(outdir, '02_stream_plot_timeline_single.jpg')
    if shwrname == "All Showers":
        binmins=1440
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
    nbins = max(len(binned)/144, 2)
    plt.locator_params(axis='x', nbins=nbins)
    #plt.xticks(rotation=0)
    # set font size
    ax = plt.gca()
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)
    # format x-axes
    x_labels = binned.index.strftime('%b-%d')
    ax.set_xticklabels(x_labels)
    ax.set(xlabel="Date", ylabel="Count")
    plt.title('Observed stream activity {}min intervals ({})'.format(binmins, shwrname))
    plt.tight_layout()

    plt.savefig(fname)
    plt.close()
    return len(dta)


def matchesGraphs(dta, shwrname, outdir, binmins=60, startdt=None, enddt=None, ticksep=24):
    logMessage('Creating matches binned graph')
    # set paper size so fonts look good
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    # add a datetime column so i can bin the data
    mdta = dta.assign(dt = pd.to_datetime(dta['_localtime'], format='_%Y%m%d_%H%M%S'))
    if startdt is not None and enddt is not None:
        mdta = mdta[mdta.dt > startdt]
        mdta = mdta[mdta.dt < enddt]

    # set the datetime to be the index
    mdta = mdta.set_index('dt')
    #select just the shower ID col
    mcountcol = mdta['_ID1']
    # resample it 
    mbinned = mcountcol.resample('{}min'.format(binmins)).count()
    mbinned.plot(kind='bar')

    # set ticks and labels every 144 intervals
    ax = plt.gca()
    nbins=len(mbinned)/24
    if nbins > 1:
        plt.locator_params(axis='x', nbins=len(mbinned)/ticksep)
        # set font size
        
        for lab in ax.get_xticklabels():
            lab.set_fontsize(SMALL_SIZE)
        
        # format x-axes
        if ticksep < 24:
            x_labels = mbinned.index.strftime('%d %H:00')
        else:
            x_labels = mbinned.index.strftime('%b-%d')

        ax.set_xticklabels(x_labels)

    ax.set(xlabel="Date", ylabel="Count")

    fname = os.path.join(outdir, '03_stream_plot_timeline_matches.jpg')
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

    fname = os.path.join(outdir, '04_stream_plot_by_correllation.jpg')
    plt.title('Number of Matched Observations ({})'.format(shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()

    nummatched = 0
    for index,row in matchgrps.items():
        nummatched += index * row

    return len(dta), nummatched


def velDistribution(dta, shwrname, outdir, vg_or_vs, binwidth=0.2):
    logMessage('Creating velocity distribution histogram')
    plt.clf()

    if vg_or_vs == 'vg':
        idx = '_vg'
        fname = '05_stream_plot_vel.jpg'
        title = 'Geocentric Velocity'
    else:
        idx = '_vs'
        fname = '06_heliocentric_velocity.jpg'
        title = 'Heliocentric Velocity'

    magdf = pd.DataFrame(dta[idx])
    bins = np.arange(10,80+binwidth,binwidth)
    magdf['bins'] = pd.cut(magdf[idx], bins=bins, labels=bins[:-1])

    _ = magdf.groupby(magdf.bins).count().plot(kind='bar', legend=None)
    ax = plt.gca()
    ax.set(xlabel='Velocity (km/s)', ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    x_labels=["%.0f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, fname)
    plt.title('{} Distribution in bins of width {} ({})'.format(title, binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return 


def durationDistribution(dta, shwrname, outdir, binwidth=0.2):
    logMessage('Creating duration distribution histogram')
    plt.clf()

    max_dist = 100 # maximum sensible value - data over this is borked

    idx = '_dur'
    fname = '13_meteor_duration.jpg'
    title = 'Duration'
    xlab = 'Seconds'

    magdf = pd.DataFrame(dta[idx])
    magdf = magdf[magdf[idx] < max_dist]
    maxlen = max(magdf[idx])
    bins = np.arange(0, maxlen + binwidth, binwidth)
    magdf['bins'] = pd.cut(magdf[idx], bins=bins, labels=bins[:-1])

    _ = magdf.groupby(magdf.bins).count().plot(kind='bar', legend=None)
    ax = plt.gca()
    ax.set(xlabel='{} (s)'.format(xlab), ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    x_labels=["%.1f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, fname)
    plt.title('{} Distribution ({})'.format(title, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return maxlen


def distanceDistribution(dta, shwrname, outdir, binwidth=1.0):
    logMessage('Creating distance distribution histogram')
    plt.clf()

    max_dist = 100 # maximum sensible value - data over this is borked

    idx = '_LD21'
    fname = '07_observed_trajectory_LD21.jpg'
    title = 'Observed Track Length'
    xlab = 'Length'

    magdf = pd.DataFrame(dta[idx])
    magdf = magdf[magdf[idx] < max_dist]
    maxlen = max(magdf[idx])
    bins = np.arange(0, maxlen + binwidth, binwidth)
    magdf['bins'] = pd.cut(magdf[idx], bins=bins, labels=bins[:-1])

    _ = magdf.groupby(magdf.bins).count().plot(kind='bar', legend=None)
    ax = plt.gca()
    ax.set(xlabel='{} (km)'.format(xlab), ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    x_labels=["%.0f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, fname)
    plt.title('{} Distribution ({})'.format(title, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return maxlen


def ablationDistribution(dta, shwrname, outdir):
    logMessage('Creating ablation zone distribution histogram')
    plt.clf()

    idx = '_H1'
    idx2 = '_H2'
    fname = '11_stream_ablation.jpg'
    title = 'Ablation Zone'

    magdf = dta[[idx, idx2]].copy()
    
    magdf = magdf[magdf[idx] < 140.0]
    magdf = magdf[magdf[idx2] > 0.0]
    magdf = magdf.sort_values(by=['_H1', '_H2'], ascending=[False, True])

    magdf.plot(kind='bar', width=1.0, alpha=1, legend=None)
    ax = plt.gca()
    ax.set(xlabel='', ylabel="km")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, fname)
    plt.title('{} Distribution ({})'.format(title, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return min(magdf[idx2])


def radiantDistribution(dta, shwrname, outdir):
    logMessage('Creating radiant scatterplot')
    plt.clf()

    idx = '_ra_o'
    idx2 = '_dc_o'
    fname = '12_stream_plot_radiant.jpg'
    title = 'Radiant Position'

    magdf = dta[[idx, idx2]].copy()
    
    magdf = magdf.sort_values(by=[idx, idx2], ascending=[False, True])

    #bins = np.arange(0,maxalt+binwidth,binwidth)
#    magdf['bins'] = pd.cut(magdf[idx], bins=bins, labels=bins[:-1])

    magdf.plot.scatter(x=idx, y=idx2)
    ax = plt.gca()
    ax.set(xlabel='RA (deg)', ylabel="Dec (deg)")
    #plt.locator_params(axis='x', nbins=12)
    #for lab in ax.get_xticklabels():
    #    lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    #x_labels=["%.0f" % number for number in bins[:-1]]
    #ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, fname)
    plt.title('{} Distribution ({})'.format(title, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return 


def semimajorDistribution(dta, shwrname, outdir, binwidth=0.5):
    logMessage('Creating semimajor axis histogram')
    plt.clf()

    magdf=pd.DataFrame(dta['_a'])
    magdf = magdf[magdf['_a'] > 0]
    magdf = magdf[magdf['_a'] < 20]
    maxval = max(magdf['_a'])
    bins=np.arange(0, maxval + binwidth,binwidth)
    magdf['bins']=pd.cut(magdf['_a'], bins=bins, labels=bins[:-1])

    _ = magdf.groupby(magdf.bins).count().plot(kind='bar', legend=None)
    ax = plt.gca()
    ax.set(xlabel="Semimajor Axis (AU)", ylabel="Count")
    plt.locator_params(axis='x', nbins=12)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(SMALL_SIZE)

    # format x-axes
    x_labels=["%.0f" % number for number in bins[:-1]]
    ax.set_xticklabels(x_labels)
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, '10_semimajoraxisfreq.jpg')
    plt.title('Semimajor Axis Distribution in bins of width {} ({})'.format(binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return 


def magDistributionAbs(dta, shwrname, outdir, binwidth=0.2):
    logMessage('Creating matches abs mag histogram')
    plt.clf()

    bestvmag = min(dta['_mag'])
    magdf=pd.DataFrame(dta['_amag'])
    bins=np.arange(-6,6+binwidth,binwidth)
    magdf['bins']=pd.cut(magdf['_amag'], bins=bins, labels=bins[:-1])

    _ = magdf.groupby(magdf.bins).count().plot(kind='bar', legend=None)
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

    fname = os.path.join(outdir, '08_stream_plot_mag.jpg')
    plt.title('Abs Magnitude Distribution in bins of width {} ({})'.format(binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return min(magdf['_amag']), bestvmag


def magDistributionVis(dta, shwrname, outdir, binwidth=0.2):
    logMessage('Creating detections visual mag histogram')

    magdf=pd.DataFrame(dta['Mag'])
    bins=np.arange(-6,6+binwidth,binwidth)
    magdf['bins']=pd.cut(magdf['Mag'], bins=bins, labels=bins[:-1])

    gd = magdf.groupby(magdf.bins).count()
    
    gd.plot(kind='bar', legend=None)
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

    fname = os.path.join(outdir, '07_stream_plot_vis_mag.jpg')
    plt.title('Visual Magnitude Distribution in bins of width {} ({})'.format(binwidth, shwrname))
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    return min(magdf['Mag'])


def showerAnalysis(shwr, dtstr):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')

    # set up paths, files etc
    # check if month was passed in
    mth = None
    if dtstr > 9999:
        ym = dtstr
        yr = int(str(dtstr)[:4])
        mth = str(ym)[4:6]
        outdir = os.path.join(datadir, 'reports', str(yr), shwr, mth)
    else:
        yr = dtstr
        outdir = os.path.join(datadir, 'reports', str(yr), shwr)
        
    os.makedirs(outdir, exist_ok=True)

    cols = ['Shwr','Dtstamp','Y','M','ID','Mag']
    filt = None
    if shwr != 'ALL':
        sl = imo.IMOshowerList()
        maxdt = sl.getEnd(shwr) + datetime.timedelta(days=10)
        mindt = sl.getStart(shwr) + datetime.timedelta(days=-10)

    # read the single-station data
    singleFile = os.path.join(datadir, 'single', f'singles-{yr}.parquet.snap')
    sngl = pd.read_parquet(singleFile, columns=cols, filters=filt)

    sngl = sngl[sngl['Y']==int(yr)] # just in case there's some pollution in the database

    # select the required data
    if shwr != 'ALL':
        id, shwrname, sl, dt = sd.getShowerDets(shwr)
        sngl = sngl[sngl['Shwr']==shwr]
        sngl = sngl[sngl.Dtstamp > mindt.timestamp()]
        sngl = sngl[sngl.Dtstamp < maxdt.timestamp()]
    else:
        shwrname = 'All Showers'

    if mth is not None:
        tmpdt = datetime.datetime.strptime(mth, '%m')
        mthname = tmpdt.strftime('%B')
        shwrname = 'All Showers, {}'.format(mthname)
        sngl = sngl[sngl['M']==int(mth)]

    numsngl = 0
    numcams = 0
    bestvmag = 0
    # now get the graphs and stats
    if len(sngl) > 0:
        numsngl = timeGraph(sngl, shwrname, outdir, 10)
        numcams = stationGraph(sngl, shwrname, outdir, 20)
        bestvmag = magDistributionVis(sngl, shwrname, outdir)
        if shwr == 'ALL':
            showerGraph(sngl, 'observed', outdir)
        pass
    sngl = None

    cols = ['_M_ut', '_stream','_Nos','_ID1','_vg','_vs','_dur','_LD21','_H1','_H2','_ra_o','_dc_o','_a','_mag','_localtime','_amag', 'dtstamp']
    filt = None
    matchfile = os.path.join(datadir, 'matched', 'matches-full-{}.parquet.snap'.format(yr))
    mtch = pd.read_parquet(matchfile, columns=cols, filters=filt)

    # select the required data
    if shwr != 'ALL':
        id, shwrname, sl, dt = sd.getShowerDets(shwr)
        mtch = mtch[mtch['_stream']==shwr]
        mtch = mtch[mtch.dtstamp > mindt.timestamp()]
        mtch = mtch[mtch.dtstamp < maxdt.timestamp()]
    else:
        shwrname = 'All Showers'

    if mth is not None:
        tmpdt = datetime.datetime.strptime(mth, '%m')
        mthname = tmpdt.strftime('%B')
        shwrname = 'All Showers, {}'.format(mthname)
        mtch = mtch[mtch['_M_ut']==int(mth)]

    nummatch = 0
    nummatched = 0
    bestamag = 0
    lowest = 0
    longest = 0
    slowest = 0

    if len(mtch) > 0:
        if shwr == 'ALL':
            binsize = 1440
        else:
            binsize = 60

        nummatch, nummatched = matchesGraphs(mtch, shwrname, outdir, binsize)
        bestamag, bestvmag = magDistributionAbs(mtch, shwrname, outdir)
        velDistribution(mtch, shwrname, outdir, 'vg')
        velDistribution(mtch, shwrname, outdir, 'vs')
        longest = distanceDistribution(mtch, shwrname, outdir)
        slowest = durationDistribution(mtch, shwrname, outdir)
        if mth is not None:
            lowest = ablationDistribution(mtch, shwrname, outdir)
        else:
            lowest = min(mtch['_H2'])
        lowest = max(0, lowest) # can't be underground
        if shwr != 'ALL':
            semimajorDistribution(mtch, shwrname, outdir)
            radiantDistribution(mtch, shwrname, outdir)
        else:
            showerGraph(mtch, 'matched', outdir)
    mtch = None

    # create summary file
    outfname = os.path.join(outdir, 'statistics.txt')
    with open(outfname,'w') as outf:
        outf.write('Summary Statistics for {} {}\n'.format(shwrname, str(yr)))
        outf.write('=======================================\n')
        outf.write('Report created: {}\n\n'.format(datetime.datetime.now().strftime('%Y-%m-%dZ%H:%M:%S')))
        if shwr != 'ALL':
            outf.write('Shower ID and Code:                {} {}\n'.format(id, shwr))
            outf.write('Date of peak:                      {}-{}\n'.format(yr, dt))
            outf.write('Solar Longitide:                   {:.2f}\n\n'.format(sl))

        outf.write('Total Single-station Detections:   {}\n'.format(numsngl))
        outf.write('Total Matched Detections:          {}\n'.format(nummatched))
        outf.write('Leading to Solved Trajectories:    {}\n'.format(nummatch))
        outf.write('Number of Cameras with Detections: {}\n'.format(numcams))
        if numsngl > 0:
            convrate = nummatched / numsngl * 100
        else:
            convrate = 0
        outf.write('Conversion Rate:                   {:.2f}%\n\n'.format(convrate))

        outf.write('Brightest Magnitude seen:          {:.2f}\n'.format(bestvmag))
        outf.write('Lowest altitude seen:              {:.2f}km\n'.format(lowest))
        outf.write('Longest track seen:                {:.2f}km\n'.format(longest))
        outf.write('Longest event seen:                {:.2f}s\n'.format(slowest))

        outf.write('\nExplanation of the data\n')
        outf.write('Single-station classifications rely on 2-dimensional analysis and are not reliable.\n')
        outf.write('Multi-station matching works in 3-D and identifies meteors missed in single-station.\n\n')
        outf.write('Events with a lowest altitude below about 30km are potential meteorite droppers\n')

    return shwrname


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python showerAnalysis.py GEM 2017')
        exit(0)
    yr=int(sys.argv[2])
    shwr = sys.argv[1]
    showerAnalysis(shwr, yr)

# to possibly add : 
# histogram of distance from radiant
# semimajor axis vs inclination and solar longitude
# abs mag vs lowest height
# abs mag vs track length
# abs mag vs lowest and highest heights
# UK map showing all detections ground tracks
# sky map showing all detections sky tracks
