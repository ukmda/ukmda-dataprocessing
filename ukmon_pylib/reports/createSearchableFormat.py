#
# python module to read data in various formats and create a format that can be searched
# with S3 SQL statements from a lambda function. The lambda is invoked from a REST API
# via the Search page on the website. 
#

import sys
import os
import numpy as np
import pandas as pd
import configparser as cfg
import datetime 
import boto3


def UFOAToSrchable(configfile, year, outdir):
    """ Convert UFO Analyser records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file

    """
    print('ufoa to searchable format')
    config=cfg.ConfigParser()
    config.read(configfile)
    weburl=config['config']['SITEURL']

    fname = 'UKMON-{:s}-single.csv'.format(year)
    rmsuafile= os.path.join(config['config']['DATADIR'], 'consolidated', fname)
    # print(rmsuafile)
    # load the data
    print('read single file to get shower and mag')
    uadata = pd.read_csv(rmsuafile, delimiter=',')

    print('read list of available jpgs')
    fname = os.path.join(outdir, 'single.csv')
    with open(fname, 'r') as inf:
        dta = inf.readlines()

    dtstamps = []
    urls = []
    imgs = []
    grps = []
    sts = []
    mags = []

    for li in dta:
        fname = os.path.basename(li).strip()
        #print(fname)
        if fname[0] == 'M':  # UFO data
            dtstr=fname[1:16]
            camid=fname[17:-5]
        else:  # RMS data
            dtstr=fname[10:25]
            camid = fname[3:9]
        dtstamp = datetime.datetime.strptime(dtstr,'%Y%m%d_%H%M%S').timestamp()

        dtstamps.append(dtstamp)
        url = weburl + '/' + li.strip()
        urls.append(url)
        imgs.append(url)
        sts.append(camid)

        # add shower ID if available
        evts = uadata[uadata['LocalTime']==dtstr]
        #evts = evts[evts['Group']!='spo']  # default is sporadic
        evts = evts[evts['Group']!='J8_TBC']  # leave unknown as sporadics
        if len(evts) > 0:
            if evts.iloc[0].Group != 'spo':
                grps.append(evts.iloc[0].Group[3:])
            else:
                grps.append('spo')
            mags.append(evts.iloc[0].Mag)
        else:
            grps.append('UNK')
            mags.append('99')
            
    # create array for source
    print('add source column')
    srcs=np.chararray(len(dtstamps), itemsize=8)
    srcs[:]='2Single'
    srcs=srcs.decode('utf-8')

    hdr='eventtime,source,shower,mag,loccam,url,img'

    # write out the converted data
    # print(len(dtstamps), len(srcs), len(grps), len(mags), len(sts))

    print('stack data and save')
    outdata = np.column_stack((dtstamps, srcs, grps, mags, sts, urls, imgs))
    outdata = np.unique(outdata, axis=0)
    fmtstr = '%s,%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    np.savetxt(outfile, outdata, fmt=fmtstr, header=hdr, comments='')


def LiveToSrchable(configfile, year, outdir):
    """ Convert ukmon-live records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    config=cfg.ConfigParser()
    config.read(configfile)

    print('live to searchable')
    dtstamps = []
    urls = []
    imgs = []
    loccam = []
    srcs = []
    shwrs = []
    zeros = []
    for q in range(1,5):
        livef='idx{:s}{:02d}.csv'.format(year, q)
        uafile = os.path.join(config['config']['DATADIR'], 'ukmonlive', livef)
        if os.path.exists(uafile):
            # load the data
            LIVEFMT=np.dtype([('ymd','U8'),('hms','U8'),('Loc_Cam','U16'),('SID','U8'),('Bri','f8')])
            uadata = np.loadtxt(uafile, delimiter=',', skiprows=0, dtype=LIVEFMT)
            uadata = np.unique(uadata)

            for li in uadata:
                dtstr = li['ymd'] + '_' + li['hms']
                ds = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
                dtstamps.append(ds.timestamp())

                if li['SID'][:3] == 'UK0':
                    lc = li['SID']
                else:
                    lc = li['Loc_Cam'] + '_' + li['SID']
                loccam.append(lc.strip())

                url='https://live.ukmeteornetwork.co.uk/M' + li['ymd'] + '_' + li['hms'] + '_' + lc + 'P.jpg'

                urls.append(url)
                imgs.append(url)
                shwrs.append('Unknown')
                srcs.append('3Live')
                zeros.append(0)

    hdr='eventtime,source,shower,mag,loccam,url,imgs'

    # write out the converted data
    outdata = np.column_stack((dtstamps,srcs, shwrs, zeros, loccam, urls,imgs))
    outdata = np.unique(outdata, axis=0)
    fmtstr = '%s,%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-liveevents.csv'.format(year))
    np.savetxt(outfile, outdata, fmt=fmtstr, header=hdr, comments='')


def MatchToSrchable(configfile, year, outdir, indexes):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        indexes (str): list of index files
        
    """
    config=cfg.ConfigParser()
    config.read(configfile)
    weburl=config['config']['SITEURL']
    
    print('match to searchable')
    path= os.path.join(config['config']['DATADIR'], 'orbits', year)

    dtstamps = []
    urls = []
    imgs = []
    shwrs = []
    mags = []
    loccams = []
    srcs = []
    for entry in indexes:
        splis = entry.split('/')
        #mthdir = splis[0]
        orbname = splis[1]
        csvfname = splis[2]
        # print(orbname, csvfname)
        fn = os.path.join(path, 'csv', csvfname)
        try: 
            with open(fn, 'r') as idxfile:
                dta = idxfile.readline()
                if dta[:3] == 'RMS':
                    spls = dta.split(',')
                    dtval = spls[2][1:]
                    ym = dtval[:6]
                    sts = spls[5][1:].strip()
                    mag = spls[7]
                    shwr = spls[25]
                    url = weburl + '/reports/' + year
                    url1 = url + '/orbits/' + ym + '/' + orbname + '/index.html'
                    url2 = url + '/orbits/' + ym + '/' + orbname + '/' + dtval + '_ground_track.png'
                    shwrs.append(shwr)
                    urls.append(url1)
                    imgs.append(url2)
                    loccams.append(sts)
                    mags.append(mag)
                    orbname = orbname.replace('-','_')[:19]
                    dtstamp = datetime.datetime.strptime(orbname, '%Y%m%d_%H%M%S.%f')
                    dtstamps.append(dtstamp.timestamp())
                    srcs.append('1Matched')
                else:
                    print('seems not RMS processed')
        except Exception:
            print('file missing {}'.format(fn))
            continue
    matchhdr='eventtime,source,shower,mag,loccam,url,img'

    # write out the converted data
    matchdata = np.column_stack((dtstamps, srcs, shwrs, mags, loccams, urls, imgs))
    matchdata = np.unique(matchdata, axis=0)
    matchfmtstr = '%s,%s,%s,%s,%s,%s,%s'

    outfile = os.path.join(outdir, '{:s}-matchedevents.csv'.format(year))
    np.savetxt(outfile, matchdata, fmt=matchfmtstr, header=matchhdr, comments='')


def createIndexOfOrbits(year):
    """ Create a list of orbit data for a whole year

    Args:
        year (int): the year to process

    Returns:
        indexes (list): a list containing the IDs of the orbits
        
    """
    indexes = []
    print('-----')
    s3 = boto3.client('s3')

    try:
        buck = os.environ['WEBSITEBUCKET']
        buck = buck[5:]
    except Exception:
        buck = 'mjmm-ukmonarchive.co.uk'

    pathstr = 'reports/' + year +'/orbits/' 
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=buck, Prefix=pathstr)
    for page in pages:
        if page.get('Contents',None):
            for obj in page['Contents']:
                if 'orbit.csv' in obj['Key'] and 'csv/' not in obj['Key']:
                    dirname = obj['Key'][len(pathstr):]
                    # print(dirname)
                    indexes.append(dirname)
    # print('-----')
    return indexes


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python createSearchableFormat.py configfile year dest')
        exit(1)
    else:
        year =sys.argv[2]

        ret = UFOAToSrchable(sys.argv[1], year, sys.argv[3])
        ret = LiveToSrchable(sys.argv[1], year, sys.argv[3])
        if int(year) > 2019:
            indexes = createIndexOfOrbits(year)
            ret = MatchToSrchable(sys.argv[1], year, sys.argv[3], indexes)
