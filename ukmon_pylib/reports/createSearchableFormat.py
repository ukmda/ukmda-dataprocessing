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


def UFOAtoSrchable(config, year, outdir):
    print(datetime.datetime.now(), 'single-detection searchable index start')
    weburl=config['config']['SITEURL']

    fname = 'UKMON-{:s}-single.csv'.format(year)
    rmsuafile = os.path.join(config['config']['DATADIR'], 'consolidated', fname)
    ####
    # rmsuafile = 'c:/temp/srchidx/UKMON-all-single.csv'
    # load the data
    print(datetime.datetime.now(), 'read single file to get shower and mag')
    uadata = pd.read_csv(rmsuafile, delimiter=',')
    uadata=uadata.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Load the list of single-camera jpgs that are available.
    print(datetime.datetime.now(), 'read list of available jpgs')
    singlesname = os.path.join(config['config']['DATADIR'], 'singleJpgs.csv')
    ####
    # singlesname = 'c:/temp/srchidx/single.csv'
    with open(singlesname, 'r') as inf:
        lis = inf.readlines()
    fnames = [x[23:-1] for x in lis]

    # filter for UFO data and create lists of the required fields
    print(datetime.datetime.now(), 'filter the UFO data')
    ukm = list(filter(lambda fnam: 'M20' in fnam, lis))
    ukmnams = list(filter(lambda fnam: 'M20' in fnam, fnames))
    ukmdts = [datetime.datetime.strptime(x[1:16],'%Y%m%d_%H%M%S').timestamp() for x in ukmnams]
    ukmdtstrs = [x[1:16] for x in ukmnams]
    ukmcamids = [x[17:-5] for x in ukmnams]
    ukmurls = [weburl + '/' + x[:-1] for x in ukm]
    ukmimgs = ukmurls

    # do the same for RMS data
    print(datetime.datetime.now(), 'filter the RMS data')
    rms = list(filter(lambda fnam: 'FF_' in fnam, lis))
    rmsnams = list(filter(lambda fnam: 'FF_' in fnam, fnames))
    rmsdts = [datetime.datetime.strptime(x[10:25],'%Y%m%d_%H%M%S').timestamp() for x in rmsnams]
    rmsdtstrs = [x[10:25] for x in rmsnams]
    rmscamids = [x[3:9] for x in rmsnams]
    rmsurls = [weburl + '/' + x[:-1] for x in rms]
    rmsimgs = rmsurls

    #concatenate the lists 
    print(datetime.datetime.now(), 'concatenate and turn into DF')
    dts = ukmdts + rmsdts
    dtstrs = ukmdtstrs + rmsdtstrs
    camids = ukmcamids + rmscamids
    urls = ukmurls + rmsurls
    imgs = ukmimgs + rmsimgs

    # create array for source
    print(datetime.datetime.now(), 'add source column')
    #srcs=np.chararray(len(dts), itemsize=8)
    #srcs[:]='2Single'
    #srcs=srcs.decode('utf-8')
    srcs = ['2Single']*len(dts)

    # and put it all in a dataframe
    print(datetime.datetime.now(), 'create interim dataframe')
    hdr=['eventtime','source','loccam','url','imgs','LocalTime']
    resdf = pd.DataFrame(zip(dts, srcs, camids, urls, imgs, dtstrs), columns=hdr)
    # now add the shower IDs and magnitudes where known

    # create dataframe containing just the columns we want from that dataset
    print(datetime.datetime.now(), 'create group and mag dataframe')
    subsetdta=[uadata['LocalTime'],uadata['Group'],uadata['Mag'], uadata['Loc_Cam']]
    grpmagdta=pd.concat(subsetdta, axis=1, keys=['LocalTime','Group','Mag','loccam'])

    # create a merged dataframe 
    print(datetime.datetime.now(), 'initial merge')
    mrg = resdf.merge(grpmagdta, how='left', on=['LocalTime','loccam'])
    print('total', len(mrg))
    got = mrg.loc[mrg.Group.notnull()]
    print('matched', len(got))

    for i in range(1, 11):
        print(datetime.datetime.now(), 'try adding ', i, ' secs on')
        mis1 = mrg.loc[mrg.Group.isnull(), ['eventtime','source','loccam','url','imgs']]
        print('missed', len(mis1))
        newtims = [datetime.datetime.fromtimestamp(x+i).strftime('%Y%m%d_%H%M%S') for x in mis1['eventtime']]
        mis1['LocalTime'] = newtims
        mrg = mis1.merge(grpmagdta, how='left', on=['LocalTime','loccam'])
        got2 = mrg[mrg.Group.notnull()]
        print('matched', len(got2))
        got = pd.concat([got, got2])

    mis = mrg.loc[mrg.Group.isnull(), ['eventtime','source','loccam','url','imgs']]

    # create array for missing data and add to dataframe
    print(datetime.datetime.now(), 'add grp,mag column to remaining missing')
    mis['Group'] = ['unk'] * len(mis)
    mis['Mag'] = [99] * len(mis)

    got = pd.concat([got, mis])

    got = got[['eventtime','source','Group','Mag','loccam','url','imgs']]

    print(datetime.datetime.now(), 'save data')
    outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    # outfile = 'c:/temp/srchidx/got.csv'
    got.to_csv(outfile, sep=',', index=False)
    print(datetime.datetime.now(), 'single-detection index created')
    return 


def LiveToSrchable(config, year, outdir):
    """ Convert ukmon-live records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    print(datetime.datetime.now(), 'live to searchable')
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


def MatchToSrchable(config, year, outdir, indexes):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        indexes (str): list of index files
        
    """
    weburl=config['config']['SITEURL']
    
    print(datetime.datetime.now(), 'match to searchable')
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
        orbname = splis[-2]
        csvfname = splis[-1]
        # print(orbname, csvfname)
        fn = os.path.join(path, 'csv', csvfname)
        try: 
            with open(fn, 'r') as idxfile:
                dta = idxfile.readline()
                if dta[:3] == 'RMS':
                    spls = dta.split(',')
                    dtval = spls[2][1:]
                    ym = dtval[:6]
                    ymd = dtval[:8]
                    sts = spls[5][1:].strip()
                    mag = spls[7]
                    shwr = spls[25]
                    url = weburl + '/reports/' + year
                    if int(year) < 2021:
                        url1 = url + '/orbits/' + ym + '/' + orbname + '/index.html'
                        url2 = url + '/orbits/' + ym + '/' + orbname + '/' + dtval + '_ground_track.png'
                    else:
                        url1 = url + '/orbits/' + ym + '/' + ymd + '/' + orbname + '/index.html'
                        url2 = url + '/orbits/' + ym + '/' + ymd + '/' + orbname + '/' + dtval + '_ground_track.png'
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
            print(datetime.datetime.now(), 'file missing {}'.format(fn))
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
    print(datetime.datetime.now(), '-----')
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
    if len(sys.argv) < 2:
        print('usage: python createSearchableFormat.py year dest')
        exit(1)
    else:
        srcdir = os.getenv('SRC')
        config = cfg.ConfigParser()
        config.read(os.path.join(srcdir, 'config', 'config.ini'))

        year =sys.argv[1]

        ret = UFOAtoSrchable(config, year, sys.argv[2])
        ret = LiveToSrchable(config, year, sys.argv[2])
        if int(year) > 2019:
            indexes = createIndexOfOrbits(year)
            ret = MatchToSrchable(config, year, sys.argv[2], indexes)
