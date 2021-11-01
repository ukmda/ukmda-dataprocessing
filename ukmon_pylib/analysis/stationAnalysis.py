#
# Python code to analyse meteor shower data
#

import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import shutil
import glob
import datetime

from wmpl.Utils.TrajConversions import jd2Date

from utils import getShowerDates as sd
from fileformats import CameraDetails as cd

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12


def getBrightest(mtch, xtra, loc, outdir, when):
    brightest = mtch[mtch['_mjd'].isin (list(xtra['mjd']))].nsmallest(10, ['_mag'])
    fbs = []
    fname = os.path.join(outdir, 'fbtable.js')
    with open(fname, 'w') as fbf:
        fbf.write('$(function() {\n')
        fbf.write('var table = document.createElement(\"table\");\n')
        fbf.write('table.className = \"table table-striped table-bordered table-hover table-condensed\";\n')
        fbf.write('var header = table.createTHead();\n')
        fbf.write('header.className = \"h4\";\n')
        for r in brightest.iterrows():
            fbs.append({'mjd': r[1]._mjd, 'mag': r[1]._mag, 'shwr':r[1]._stream})
            dt = jd2Date(r[1]._mjd + 2400000.5, dt_obj=True)
            dtstr = dt.strftime('%Y%m%d_%H%M%S')
            ms = int(dt.microsecond/1000)
            suff = '.{:03d}_UK'.format(ms)
            dtstr = dtstr + suff
            yr = dtstr[:4]
            ym = dtstr[:6]
            ymd = dtstr[:8]
            mag = r[1]._mag
            shwr = r[1]._stream
            fbf.write('var row = table.insertRow(-1);\n')
            fbf.write('var cell = row.insertCell(0);\n')
            hlink='/reports/{}/orbits/{}/{}/{}/index.html'.format(yr, ym, ymd, dtstr)
            fbf.write('cell.innerHTML = "<a href={}>{}</a>";\n'.format(hlink, dtstr))
            fbf.write('var cell = row.insertCell(1);\n')
            fbf.write('cell.innerHTML = "{}";\n'.format(mag))
            fbf.write('var cell = row.insertCell(2);\n')
            fbf.write('cell.innerHTML = "{}";\n'.format(shwr))

        fbf.write('var row = header.insertRow(0);\n')
        fbf.write('var cell = row.insertCell(0);\n')
        fbf.write('cell.innerHTML = "DateTime";\n')
        fbf.write('cell.className = "small";\n')
        fbf.write('var cell = row.insertCell(1);\n')
        fbf.write('cell.innerHTML = "Magnitude";\n')
        fbf.write('cell.className = "small";\n')
        fbf.write('var cell = row.insertCell(2);\n')
        fbf.write('cell.innerHTML = "Shower";\n')
        fbf.write('cell.className = "small";\n')
        fbf.write('var outer_div = document.getElementById(\"fbtable\");\n')
        fbf.write('outer_div.appendChild(table);\n')
        fbf.write('})\n')

    return fbs


def timeGraph(dta, loc, outdir, when, sampleinterval):
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
    binned = countcol.resample('{}'.format(sampleinterval)).count()
    binned.plot(kind='bar')

    # set ticks and labels every 144 intervals
    if len(binned) > 288:
        plt.locator_params(axis='x', nbins=len(binned)/144)
    else: 
        plt.locator_params(axis='x', nbins=len(binned))
    
    ax = plt.gca()

    # format x-axes
    ax.set(xlabel="Date", ylabel="Count")
    x_labels = binned.index.strftime('%b-%d')
    try: 
        ax.set_xticklabels(x_labels)

        for lab in ax.get_xticklabels():
            lab.set_fontsize(SMALL_SIZE)
    except:
        pass        

    fname = os.path.join(outdir, 'station_plot_timeline_single.jpg')
    plt.title('Observed stream activity {} intervals for {} in {}'.format(sampleinterval, loc, when))
    try:
        plt.tight_layout()
        plt.savefig(fname)
        return 'station_plot_timeline_single.jpg'
    except:
        return ''


def shwrGraph(dta, loc, outdir, when):
    print('Creating showers by station')
    plt.clf()

    dta1 = dta[dta['Shwr']!='spo']
    if len(dta1) > 0:
        dta = dta1
    dta.groupby('Shwr').count().sort_values(by='Ver', ascending=True).Ver.plot.barh()

    ax = plt.gca()
    ax.set(xlabel="Count", ylabel="Shower")
    fig = plt.gcf()
    fig.set_size_inches(11.6, 8.26)

    fname = os.path.join(outdir, 'showers_by_station.jpg')
    plt.title('Shower meteors observed by {} in {}'.format(loc, when))
    plt.tight_layout()
    plt.savefig(fname)

    return 'showers_by_station.jpg'


def reportOneSite(ym, loc):
    yr = int(ym[:4])
    when = ym[:4]
    mth = None
    if len(ym) > 4:
        mth = int(ym[4:6])
        when = '{:02d}-{}'.format(mth, yr)

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    srcdir = os.getenv('SRC')
    if srcdir is None:
        print('define SRC first')
        exit(1)

    # set up paths, files etc
    if mth is None: 
        sampleinterval="1M"
        outdir = os.path.join(datadir, 'reports', str(yr), 'stations', loc)
    else:
        sampleinterval="30min"
        outdir = os.path.join(datadir, 'reports', str(yr), 'stations', loc, '{:02d}'.format(mth))
    os.makedirs(outdir, exist_ok=True)
    idxfile = os.path.join(outdir,'index.html')
    shutil.copyfile(os.path.join(srcdir,'website/templates/header.html'), idxfile)
    outf = open(idxfile, 'a+')
    if mth is not None:
        outf.write('<a href=../index.html>back to index for {}</a><br>\n'.format(loc))
        mthno = int(mth)    
        if mthno > 1:
            prvmth = '{:02d}'.format(mthno-1)
            outf.write('<a href=../{}/index.html>Previous Month</a><br>\n'.format(prvmth)) 
        if mthno < 12:
            nxtmth = '{:02d}'.format(mthno+1)
            outf.write('<a href=../{}/index.html>Next Month</a><br>\n'.format(nxtmth)) 

    else:
        outf.write('<a href=../index.html>back to Station index</a>\n')

    outf.write('<h2>Station report for {} for {}</h2>\n'.format(loc, when))
    outf.write('Last updated: {}<br>'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    singleFile = os.path.join(datadir, 'single', 'singles-{}.csv'.format(yr))
    matchfile = os.path.join(datadir, 'matched', 'matches-{}.csv'.format(yr))
    extrafile = os.path.join(datadir, 'matched', 'matches-extras-{}.csv'.format(yr))

    # read the data
    sngl = pd.read_csv(singleFile)
    mtch = pd.read_csv(matchfile, skipinitialspace=True)
    xtra = pd.read_csv(extrafile, skipinitialspace=True)
    xtra = xtra.dropna(subset=['stations'])

    cifile = os.getenv('CAMINFO')
    if cifile is None:
        si = cd.SiteInfo()
    else:
        si = cd.SiteInfo(cifile)
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
    outf.write('During this period, {} single station detections were collected '.format(numsngl))
    outf.write(' by cameras in {}. including {} sporadics.\n'.format(loc, len(statfltr[statfltr['Shwr']=='spo'])))
    if numsngl > 0:
        tgname = timeGraph(statfltr, loc, outdir, when, sampleinterval)
        sgname = shwrGraph(statfltr, loc, outdir, when)
    else:
        tgname = None
        sgname = None
    nummatch = len(xtrafltr)
    outf.write('{} of the detections matched with other stations. '.format(nummatch))
    if nummatch > 0:
        outf.write(' Orbit and trajectory solutions were calculated for these matches. \n')
        fbs = getBrightest(mtch, xtrafltr, loc, outdir, when)
        outf.write('The brighest up to ten confirmed matches are shown below.<br>\n')
        outf.write('<div id="fbtable" class="table-responsive"></div>')
        outf.write('<script src="./fbtable.js"></script><hr>\n')

    if tgname is not None:
        outf.write('<a href=./{}><img src=./{} width=40%></a>\n'.format(tgname, tgname))
    if sgname is not None:
        outf.write('<a href=./{}><img src=./{} width=40%></a>\n'.format(sgname, sgname))
    outf.write('<hr>The graphs can be clicked on for an enlarged view.<br>\n')

    # links to monthly reports
    if mth is None:
        outf.write('<h3>Monthly reports</h3>monthly reports can be found at the links below<br>')
        outf.write('<div id="mthtable" class="table-responsive"></div>\n')
        outf.write('<script src="./mthtable.js"></script><hr>\n')
        mfname = os.path.join(outdir, 'mthtable.js')
        with open(mfname, 'w') as mthf:
            mthf.write('$(function() {\n')
            mthf.write('var table = document.createElement(\"table\");\n')
            mthf.write('table.className = \"table table-striped table-bordered table-hover table-condensed\";\n')
            #mthf.write('var header = table.createTHead();\n')
            #mthf.write('header.className = \"h4\";\n')

            mthstodo=sorted(glob.glob1(outdir, '*'))
            for m in mthstodo:
                if os.path.isdir(os.path.join(outdir, m)):
                    if (m =='01' or m=='07'):
                        mthf.write('var row = table.insertRow(-1);\n')
                    mthf.write('var cell = row.insertCell(-1);\n')
                    mthf.write('cell.innerHTML = "<a href=./{}/index.html>{}</a>";\n'.format(m, m))

            mthf.write('var outer_div = document.getElementById(\"mthtable\");\n')
            mthf.write('outer_div.appendChild(table);\n')
            mthf.write('})\n')

    with open(os.path.join(srcdir,'website/templates/footer.html'), 'r') as inf:
        lis = inf.readlines()
    outf.writelines(lis)
    outf.close()
    return numsngl, nummatch


def reportAllSites(ym):
    cifile = os.getenv('CAMINFO')
    if cifile is None:
        si = cd.SiteInfo()
    else:
        si = cd.SiteInfo(cifile)
    sitelist = si.getSites()
    for site in sitelist:
        print('processing', site)
        reportOneSite(ym, site)

    return 


if __name__ == '__main__':
    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    if len(sys.argv) < 1:
        print('usage: python stationAnalysis.py 201710 {site}')
        exit(0)
        
    ym=sys.argv[1]
    if len(sys.argv) < 3:
        reportAllSites(ym)
    else:
        loc = sys.argv[2]
        numsngl, nummatch = reportOneSite(ym, loc)
        print(numsngl, nummatch)


