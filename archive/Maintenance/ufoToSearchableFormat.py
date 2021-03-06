#
# python module to read data in UFOA format and create a format that can be searched
# with S3 sql statements
#

import sys
import os
import numpy as np
import Formats.UAFormats as uaf
import configparser as cfg
import datetime 
#import glob
import boto3


def UFOAToSrchable(configfile, year, outdir):
    config=cfg.ConfigParser()
    config.read(configfile)
    weburl=config['config']['SITEURL']
    
    fname = 'UKMON-{:s}-single.csv'.format(year)
    rmsuafile= os.path.join(config['config']['RCODEDIR'], 'DATA', 'consolidated', fname)

    # load the data
    uadata = np.loadtxt(rmsuafile, delimiter=',', skiprows=1, dtype=uaf.UFOCSV)
    uadata = np.unique(uadata, axis=0)

    # create array for source
    srcs=np.chararray(len(uadata), itemsize=8)
    srcs[:]='Single'
    srcs=srcs.decode('utf-8')

    dtstamps = []
    urls = []
    imgs = []
    for li in uadata:
        se = float(li['Sec'])
        ss = int(np.floor(se))
        us = int((se -ss)*1000000)
        if ss == 60:
            ss = 59
            us = 999999

        ds = datetime.datetime(li['Yr'], li['Mth'], li['Day'], li['Hr'], li['Min'], ss, microsecond=us)
        dtstamps.append(np.round(ds.timestamp(),2))
        ymd = '{:04d}{:02d}{:02d}'.format(li['Yr'], li['Mth'], li['Day'])
        hms = '{:02d}{:02d}{:02d}'.format(li['Hr'], li['Min'], ss)
        lc = li['Loc_Cam'].strip()
        mth = '{:04d}{:02d}'.format(li['Yr'], li['Mth'])
        fldr = '/img/single/{:04d}/{:s}/M{:s}_{:s}_{:s}P.jpg'.format(li['Yr'], mth, ymd, hms, lc)
        url = weburl + fldr
        urls.append(url)
        imgs.append(url)

    hdr='eventtime,source,shower,mag,loccam,url,img'

    # write out the converted data
    outdata = np.column_stack((dtstamps,srcs, uadata['Group'], uadata['Mag'], uadata['Loc_Cam'], urls, imgs))
    outdata = np.unique(outdata, axis=0)
    fmtstr = '%s,%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    np.savetxt(outfile, outdata, fmt=fmtstr, header=hdr, comments='')


def LiveToSrchable(configfile, year, outdir):
    config=cfg.ConfigParser()
    config.read(configfile)

    dtstamps = []
    urls = []
    imgs = []
    loccam = []
    srcs = []
    shwrs = []
    zeros = []
    for q in range(1,5):
        livef='idx{:s}{:02d}.csv'.format(year, q)
        uafile = os.path.join(config['config']['RCODEDIR'], 'DATA', 'ukmonlive', livef)
        if os.path.exists(uafile):
            # load the data
            LIVEFMT=np.dtype([('ymd','U8'),('hms','U8'),('Loc_Cam','U16'),('SID','U8'),('Bri','f8')])
            uadata = np.loadtxt(uafile, delimiter=',', skiprows=0, dtype=LIVEFMT)
            uadata = np.unique(uadata)

            for li in uadata:
                dtstr = li['ymd'] + '_' + li['hms']
                ds = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
                dtstamps.append(ds.timestamp())

                lc = li['Loc_Cam'] + '_' + li['SID']
                loccam.append(lc)

                url='https://live.ukmeteornetwork.co.uk/M' + li['ymd'] + '_' + li['hms'] + '_' + lc + 'P.jpg'

                urls.append(url)
                imgs.append(url)
                shwrs.append('Unknown')
                srcs.append('Live')
                zeros.append(0)

    hdr='eventtime,source,shower,mag,loccam,url,imgs'

    # write out the converted data
    outdata = np.column_stack((dtstamps,srcs, shwrs, zeros, loccam, urls,imgs))
    outdata = np.unique(outdata, axis=0)
    fmtstr = '%s,%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-liveevents.csv'.format(year))
    np.savetxt(outfile, outdata, fmt=fmtstr, header=hdr, comments='')


def MatchToSrchable(configfile, year, outdir, indexes):
    config=cfg.ConfigParser()
    config.read(configfile)
    weburl=config['config']['SITEURL']
    
    path= os.path.join(config['config']['RCODEDIR'], 'DATA', 'orbits', year)

    dtstamps = []
    urls = []
    imgs = []
    shwrs = []
    mags = []
    loccams = []
    srcs = []
    for entry in indexes:
        splis = entry.split('/')
        mthdir = splis[0]
        orbname = splis[1]
        csvfname = splis[2]
        print(orbname, csvfname)
        fn = os.path.join(path, 'csv', csvfname)
        print(fn)
        try: 
            with open(fn, 'r') as idxfile:
                dta = idxfile.readline()
                if dta[:3] == 'RMS':
                    spls = dta.split(',')
                    dtval = spls[2][1:]
                    ym = dtval[:6]
                    sts = spls[5][1:]
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

                    dtstamp = datetime.datetime.strptime(orbname, '%Y%m%d-%H%M%S.%f')
                    dtstamps.append(dtstamp.timestamp())
                    srcs.append('Matched')
        except Exception:
            print('broken')
            continue
    matchhdr='eventtime,source,shower,mag,loccam,url,img'

    # write out the converted data
    matchdata = np.column_stack((dtstamps, srcs, shwrs, mags, loccams, urls, imgs))
    matchdata = np.unique(matchdata, axis=0)
    matchfmtstr = '%s,%s,%s,%s,%s,%s,%s'

    outfile = os.path.join(outdir, '{:s}-matchedevents.csv'.format(year))
    np.savetxt(outfile, matchdata, fmt=matchfmtstr, header=matchhdr, comments='')


def createIndexOfOrbits(year):
    indexes = []
    print('-----')
    s3 = boto3.client('s3')
    buck = 'ukmeteornetworkarchive'
    pathstr = 'reports/' + year +'/orbits/' 
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=buck, Prefix=pathstr)
    for page in pages:
        if page.get('Contents',None):
            for obj in page['Contents']:
                if 'orbit.csv' in obj['Key'] and 'csv/' not in obj['Key']:
                    dirname = obj['Key'][len(pathstr):]
                    print(dirname)
                    indexes.append(dirname)
    print('-----')
    return indexes


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python UFOtoSearchableFormat.py configfile year dest')
        exit(1)
    else:
        year =sys.argv[2]

        ret = UFOAToSrchable(sys.argv[1], year, sys.argv[3])
        ret = LiveToSrchable(sys.argv[1], year, sys.argv[3])
        if int(year) > 2019:
            indexes = createIndexOfOrbits(year)
            ret = MatchToSrchable(sys.argv[1], year, sys.argv[3], indexes)
