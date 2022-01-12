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

from wmpl.Utils.TrajConversions import jd2Date
from fileformats import CameraDetails as cd


def convertUFOAtoSrchable(config, year, outdir):
    print(datetime.datetime.now(), 'single-detection searchable index start')
    weburl=config['config']['SITEURL']

    # load the single-station combined data
    rmsuafile = os.path.join(config['config']['DATADIR'], 'single', 'singles-{}.csv'.format(year))
    print(datetime.datetime.now(), 'read single file to get shower and mag')
    uadata = pd.read_csv(rmsuafile, delimiter=',')    
    uadata = uadata.assign(ts = pd.to_datetime(uadata['Dtstamp'], unit='s', utc=True))
    uadata['LocalTime'] = [ts.strftime('%Y%m%d_%H%M%S') for ts in uadata.ts]

    # create dataframe containing just the columns we want from that dataset
    print(datetime.datetime.now(), 'create group and mag dataframe')
    subsetdta=[uadata['LocalTime'],uadata['Shwr'],uadata['Mag'], uadata['ID']]
    grpmagdta=pd.concat(subsetdta, axis=1, keys=['LocalTime','Group','Mag','loccam'])

    # fix up the UFO camera IDs
    si = cd.SiteInfo()
    ufocams = si.getUFOCameras()
    for cam in ufocams:
        ufocam = cam['ufoid']
        dummycode = cam['dummycode']
        grpmagdta.loc[grpmagdta.loccam==dummycode, 'loccam'] = ufocam

    # Load the list of single-camera jpgs that are available.
    print(datetime.datetime.now(), 'read list of available jpgs')
    singlesname = os.path.join(config['config']['DATADIR'], 'singleJpgs-{}.csv'.format(year))
    ####
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
    rmsdts = [datetime.datetime.strptime(x[10:29],'%Y%m%d_%H%M%S_%f').timestamp() for x in rmsnams]
    rmsdtstrs = [x[10:29] for x in rmsnams]
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
    srcs = ['2Single']*len(dts)

    # and put it all in a dataframe
    print(datetime.datetime.now(), 'create interim dataframe')
    hdr=['eventtime','source','loccam','url','imgs','LocalTime']
    resdf = pd.DataFrame(zip(dts, srcs, camids, urls, imgs, dtstrs), columns=hdr)

    # fix up some mangled historical data
    resdf.loc[resdf.loccam=='Ringwood_N_UK000S', 'loccam'] = 'UK000S'
    resdf.loc[resdf.loccam=='Tackley_SW_UK0006', 'loccam'] = 'UK0006'

    # now add the shower IDs and magnitudes where known
    # create a merged dataframe 
    print(datetime.datetime.now(), 'initial merge')
    mrg = resdf.merge(grpmagdta, how='left', on=['LocalTime','loccam'])
    print('total', len(mrg))
    got = mrg.loc[mrg.Group.notnull()]
    print('matched', len(got))

    # the datestamp on the jpg may be up to ten seconds out from the actual time of the
    # meteor, because RMS records in 10-second blocks of time, and UFO is erratic. 
    for i in range(-5, 20):
        mis1 = mrg.loc[mrg.Group.isnull(), ['eventtime','source','loccam','url','imgs']]
        print('missed', len(mis1))
        print(datetime.datetime.now(), 'try adding ', i, ' secs on')
        newtims = [datetime.datetime.fromtimestamp(x+i).strftime('%Y%m%d_%H%M%S') for x in mis1['eventtime']]
        mis1['LocalTime'] = newtims
        mrg = mis1.merge(grpmagdta, how='left', on=['LocalTime','loccam'])
        got2 = mrg[mrg.Group.notnull()]
        print('matched', len(got2))
        got = pd.concat([got, got2])

    mis = mrg.loc[mrg.Group.isnull(), ['eventtime','source','loccam','url','imgs']]
    print('still missed', len(mis))

    # create array for missing data and add to dataframe
    print(datetime.datetime.now(), 'add grp,mag column to remaining missing')
    mis['Group'] = ['unk'] * len(mis)
    mis['Mag'] = [99] * len(mis)

    got = pd.concat([got, mis])

    got = got[['eventtime','source','Group','Mag','loccam','url','imgs']]

    got = got.rename(columns={'Group':'shower'})

    print(datetime.datetime.now(), 'save data')
    outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    
    got.to_csv(outfile, sep=',', index=False)
    print(datetime.datetime.now(), 'single-detection index created')
    return 


def convertLiveToSrchable(config, year, outdir):
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


def createMergedMatchFile(config, year, outdir):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    weburl=config['config']['SITEURL'] + '/reports/' + year + '/orbits/'

    matchfile = os.path.join(config['config']['DATADIR'], 'matched', 'matches-{}.csv'.format(year))
    extrafile = os.path.join(config['config']['DATADIR'], 'matched', 'matches-extras-{}.csv'.format(year))
    mtch = pd.read_csv(matchfile, skipinitialspace=True)
    xtra = pd.read_csv(extrafile, skipinitialspace=True)

    # add datestamp and source arrays, then construct required arrays
    mtch['dtstamp'] = [jd2Date(x+2400000.5, dt_obj=True).timestamp() for x in mtch['_mjd']]
    mtch['orbname'] = [datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S.%f')[:19]+'_UK' for ts in mtch['dtstamp']]

    mtch['src'] = ['1Matched' for x in mtch['_mjd']]
    mths = [x[1:7]+'/'+x[1:9] for x in mtch['_localtime']]
    gtnames = ['/' + x[1:] + '_ground_track.png' for x in mtch['_localtime']]
    mtch['url'] = [weburl + y + '/' + x + '/index.html' for x,y in zip(mtch['orbname'], mths)]
    mtch['img'] = [weburl + y + '/' + x + g for x,y,g in zip(mtch['orbname'], mths, gtnames)]

    mtch.set_index(['_mjd'])
    xtra.set_index(['mjd'])
    newm = mtch.join(xtra)

    outfile = os.path.join(outdir, 'matches-full-{}.csv'.format(year))
    newm.to_csv(outfile, index=False)

    return newm


def convertMatchToSrchable(config, year, outdir):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """

    newm = createMergedMatchFile(config, year, outdir)

    outdf = pd.concat([newm['dtstamp'], newm['src'], newm['_stream'], newm['_mag'], newm['stations'], newm['url'], newm['img']], 
        axis=1, keys=['eventtime','source','shower','mag','loccam','url','img'])
    outfile = os.path.join(outdir, '{:s}-matchedevents.csv'.format(year))
    outdf.to_csv(outfile, index=False)
    return 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python createSearchableFormat.py year dest')
        exit(1)
    else:
        srcdir = os.getenv('SRC')
        config = cfg.ConfigParser()
        config.read(os.path.join(srcdir, 'config', 'config.ini'))

        year =sys.argv[1]

        ret = convertUFOAtoSrchable(config, year, sys.argv[2])
        ret = convertLiveToSrchable(config, year, sys.argv[2])
        if int(year) > 2019:
            ret = convertMatchToSrchable(config, year, sys.argv[2])
