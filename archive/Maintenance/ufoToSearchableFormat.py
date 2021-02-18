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


def UFOAToSrchable(year, rmsuafile, outdir):
    # load the RMS data
    uadata = np.loadtxt(rmsuafile, delimiter=',', skiprows=1, dtype=uaf.UFOCSV)
    uadata = np.unique(uadata)

    # create array for source
    srcs=np.chararray(len(uadata), itemsize=8)
    srcs[:]='Single'
    srcs=srcs.decode('utf-8')

    dtstamps = []
    urls = []
    for li in uadata:
        se = float(li['Sec'])
        ss = int(np.floor(se))
        us = int((se -ss)*1000000)
        if ss == 60:
            ss = 59
            us = 999999

        ds = datetime.datetime(li['Yr'], li['Mth'], li['Day'], li['Hr'], li['Min'], ss, microsecond=us)
        dtstamps.append(np.round(ds.timestamp(),2))

        urls.append('https://somewhere')

    hdr='timestamp,Source,Shower,Mag,Loc_Cam,url'

    # write out the converted data
    UAdata = np.column_stack((dtstamps,srcs, uadata['Group'], uadata['Mag'], uadata['Loc_Cam'], urls))
    fmtstr = '%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    np.savetxt(outfile, UAdata, fmt=fmtstr, header=hdr, comments='')


def LiveToSrchable(year, rmsuafile, outdir):
    # load the data
    LIVEFMT=np.dtype([('ymd','U8'),('hms','U8'),('Loc_Cam','U16'),('SID','U8'),('Bri','f8')])
    uadata = np.loadtxt(rmsuafile, delimiter=',', skiprows=0, dtype=LIVEFMT)
    uadata = np.unique(uadata)

    # create array for source
    srcs=np.chararray(len(uadata), itemsize=8)
    srcs[:]='Live'
    srcs=srcs.decode('utf-8')

    # create array for showers
    shwrs=np.chararray(len(uadata), itemsize=8)
    shwrs[:]='Unknown'
    shwrs=shwrs.decode('utf-8')

    dtstamps = []
    urls = []
    loccam=[]
    for li in uadata:
        dtstr = li['ymd'] + '_' + li['hms']
        ds = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
        dtstamps.append(ds.timestamp())

        lc = li['Loc_Cam'] + '_' + li['SID']
        loccam.append(lc)

        url='https://live.ukmeteornetwork.co.uk/M' + li['ymd'] + '_' + li['hms'] + '_' + lc + 'P.jpg'

        urls.append(url)

    # create arrays of zeros to put in the unused columns
    zeros=np.zeros(len(uadata))

    hdr='timestamp,Source,Shower,Mag,Loc_Cam,url'

    # write out the converted data
    UAdata = np.column_stack((dtstamps,srcs, shwrs, zeros, loccam, urls))
    fmtstr = '%s,%s,%s,%s,%s,%s'
    outfile = os.path.join(outdir, '{:s}-liveevents.csv'.format(year))
    np.savetxt(outfile, UAdata, fmt=fmtstr, header=hdr, comments='')


def MatchToSrchable(configfile, year, outdir):
    config=cfg.ConfigParser()
    config.read(configfile)
    
    path= os.path.join(config['config']['RCODEDIR'], 'DATA', 'orbits', year, 'csv')
    listOfFiles = os.listdir(path)

    dtstamps = []
    urls = []
    shwrs = []
    mags = []
    loccams = []
    srcs = []
    for entry in listOfFiles:
        orbname = entry[:22]
        print(orbname)
        fname = os.path.join(config['config']['RCODEDIR'], 'DATA', 'orbits', year, 'csv', entry)
        with open(fname, 'r') as fi:
            dta = fi.readline()
            if dta[:3] == 'RMS':
                spls = dta.split(',')
                dtval = spls[2][1:]
                ym = dtval[:6]
                sts = spls[5][1:]
                mag = spls[7]
                shwr = spls[25]

                # reports/2021/orbits/202102/20210204-003908.447008/20210204_003916_orbit_top.png
                url = 'https://archive.ukmeteornetwork.co.uk/reports/' + year
                url = url + '/orbits/' + ym + '/' + orbname + '/' + dtval + '_ground_track.png'
                shwrs.append(shwr)
                urls.append(url)
                loccams.append(sts)
                mags.append(mag)

                dtstamp = datetime.datetime.strptime(orbname, '%Y%m%d-%H%M%S.%f')
                dtstamps.append(dtstamp.timestamp())
                srcs.append('Matched')
    matchhdr='timestamp,Source,Shower,Mag,Loc_Cam,url'

    # write out the converted data
    matchdata = np.column_stack((dtstamps, srcs, shwrs, mags, loccams, urls))
    matchfmtstr = '%s,%s,%s,%s,%s,%s'

    outfile = os.path.join(outdir, '{:s}-matchedevents.csv'.format(year))
    np.savetxt(outfile, matchdata, fmt=matchfmtstr, header=matchhdr, comments='')


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: python UFOtoSearchableFormat.py configfile singlefile livefile dest')
        exit(1)
    else:
        idxname = os.path.basename(sys.argv[3])
        year = idxname[3:7]

        ret = UFOAToSrchable(year, sys.argv[2], sys.argv[4])
        ret = LiveToSrchable(year, sys.argv[3], sys.argv[4])
        ret = MatchToSrchable(sys.argv[1], year, sys.argv[4])
