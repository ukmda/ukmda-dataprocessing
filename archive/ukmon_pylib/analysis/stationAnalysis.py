#
# Python code to analyse meteor shower data
#
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import os
import pandas as pd
from matplotlib import pyplot as plt
import shutil
import datetime
import boto3

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12


def getBrightest(mtch, xtra, loc, outdir, when):
    brightest = mtch[mtch['_mjd'].isin(list(xtra['mjd']))].drop_duplicates(subset=['_mjd', '_mag'], keep='last')
    brightest = brightest.nsmallest(10, ['_mag'])
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
            orbname = r[1].orbname
            yr = orbname[:4]
            ym = orbname[:6]
            ymd = orbname[:8]
            mag = r[1]._mag
            shwr = r[1]._stream
            fbf.write('var row = table.insertRow(-1);\n')
            fbf.write('var cell = row.insertCell(0);\n')
            hlink='/reports/{}/orbits/{}/{}/{}/index.html'.format(yr, ym, ymd, orbname)
            fbf.write('cell.innerHTML = "<a href={}>{}</a>";\n'.format(hlink, orbname))
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
        plt.close()
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
    plt.close()

    return 'showers_by_station.jpg'


def reportOneSite(yr, mth, loc, sngl, mful, idlist, outdir):
    print(f'processing {loc}')
    when = f'{yr}'
    if mth is not None:
        when = f'{mth:02d}-{yr}'

    idxfile = os.path.join(outdir,'index.html')
    templatedir=os.getenv('TEMPLATES', default='/home/ec2-user/prod/website/templates')

    shutil.copyfile(os.path.join(templatedir, 'header.html'), idxfile)
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

    # select the required data
    statfltr = sngl[sngl['ID'].isin(idlist)]
    xtrafltr = pd.DataFrame()
    for id in idlist:
        xtmp = mful[mful['stations'].str.contains(id)]    
        xtrafltr =pd.concat([xtrafltr,xtmp]).drop_duplicates()
    
    if mth is not None:
        if len(statfltr) > 0:
            statfltr = statfltr[statfltr['M']==mth]
        if len(xtrafltr) > 0:
            xtrafltr = xtrafltr[xtrafltr['_M_ut']==mth]

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
        _ = getBrightest(mful, xtrafltr, loc, outdir, when)
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

            currmth = datetime.datetime.now().month
            if yr < datetime.datetime.now().year:
                currmth = 12
                
            for m in range(1,currmth+1):
                if m == 1 or m== 7:
                    mthf.write('var row = table.insertRow(-1);\n')
                mthf.write('var cell = row.insertCell(-1);\n')
                mthf.write(f'cell.innerHTML = "<a href=./{m:02d}/index.html>{m:02d}</a>";\n')

            mthf.write('var outer_div = document.getElementById(\"mthtable\");\n')
            mthf.write('outer_div.appendChild(table);\n')
            mthf.write('})\n')

    with open(os.path.join(templatedir, 'footer.html'), 'r') as inf:
        lis = inf.readlines()
    outf.writelines(lis)
    outf.close()
    return numsngl, nummatch


def getExtraArgs(fname):
    _, file_ext = os.path.splitext(fname)
    ctyp='text/html'
    if file_ext=='.jpg': 
        ctyp = 'image/jpeg'
    elif file_ext=='.png': 
        ctyp = 'image/png'
    elif file_ext=='.js': 
        ctyp = 'text/javascript'
    extraargs = {'ContentType': ctyp}
    return extraargs


def pushToWebsite(fuloutdir, outdir, websitebucket):

    sts_client = boto3.client('sts')
    acct=sts_client.get_caller_identity().get('Account')
    if acct == '317976261112':
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::183798037734:role/service-role/S3FullAccess",
            RoleSessionName="AssumeRoleSession1")
        
        credentials=assumed_role_object['Credentials']
        
        # Use the temporary credentials that AssumeRole returns to connections
        s3 = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    else:
        s3 = boto3.resource('s3')
    
    flist = os.listdir(fuloutdir)
    for fi in flist:
        locfname = fuloutdir + '/' + fi
        key = outdir + '/' + fi
        if os.path.isfile(locfname):
            #print(locfname, key)
            extraargs = getExtraArgs(fi)
            s3.meta.client.upload_file(locfname, websitebucket, key, ExtraArgs=extraargs) 
    return 


if __name__ == '__main__':

    if len(sys.argv) < 1:
        print('usage: python stationAnalysis.py 201710 {site}')
        exit(0)
        
    ym=sys.argv[1]

    mth = None
    if len(ym) > 4:
        mth = int(ym[4:6])

    # set up paths, files etc
    yr = int(ym[:4])
        
    matchcols = ['_Y_ut','_M_ut','_mag','_mjd','mjd','_stream','orbname','stations']
    snglcols = ['ID','Shwr','Dtstamp','Ver', 'M', 'Y']
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    cifile = os.path.join(datadir,'consolidated','camera-details.csv')
    
    sngl = pd.read_parquet(os.path.join(datadir, 'single', f'singles-{yr}.parquet.snap'), columns=snglcols)
    mful = pd.read_parquet(os.path.join(datadir, 'matched', f'matches-full-{yr}.parquet.snap'), columns=matchcols)
    camlist = pd.read_csv(cifile)

    sngl = sngl[sngl['Y']==int(yr)] # just in case there's some pollution in the database
    mful = mful[mful['_Y_ut']==int(yr)] 

    if len(sys.argv) > 2:
        locs = [sys.argv[2]]
    else:
        locs = list(camlist[camlist.active==1].site.drop_duplicates().sort_values())

    for loc in locs: 
        camlistfltr = camlist[camlist.site == loc]
        camlistfltr = camlistfltr[camlistfltr.active == 1]
        # use dummycode here to find data for both UFO and RMS cams
        idlist = list(camlistfltr.dummycode) 

        if mth is None:
            sampleinterval="1M"
            shortoutdir = os.path.join('reports', str(yr), 'stations', loc)
            outdir = os.path.join(datadir, shortoutdir)
        else:
            sampleinterval="30min"
            shortoutdir = os.path.join('reports', str(yr), 'stations', loc, f'{mth:02d}')
            outdir = os.path.join(datadir, shortoutdir)

        os.makedirs(outdir, exist_ok=True)

        numsngl, nummatch = reportOneSite(yr, mth, loc, sngl, mful, idlist, outdir)
