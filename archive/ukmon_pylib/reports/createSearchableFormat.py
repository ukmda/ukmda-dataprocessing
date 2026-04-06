# Copyright (C) 2018-2023 Mark McIntyre
#
# python module to read data in various formats and create a format that can be searched
# with S3 SQL statements from a lambda function. The lambda is invoked from a REST API
# via the Search page on the website. 
#

import sys
import os
import pandas as pd
import datetime 
import boto3


def checkUrl(s3, url):
    siteroot = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')
    retval = url
    tmpurl = url
    if url[0]==',':
        tmpurl = url[1:]
    try:
        _ = s3.head_object(Bucket=siteroot[5:], Key=tmpurl[1:])
    except Exception:
        #print(e)
        retval = '/img/missing-white.png'
    print(url, retval)
    return retval


def convertSingletoSrchable(datadir, year, newonly=True):
    print(datetime.datetime.now(), 'single-detection searchable index start')
    s3 = boto3.client('s3')

    # load the single-station combined data
    if newonly is False:
        rmsuafile = os.path.join(datadir, 'single', f'singles-{year}.parquet.snap')
    else:
        rmsuafile = os.path.join(datadir, 'single', f'singles-{year}-new.parquet.snap')
    print(datetime.datetime.now(), f'read single file to get shower and mag: {rmsuafile}')
    cols = ['Dtstamp','Shwr','Mag','ID','Y','M','Filename']
    if not os.path.isfile(rmsuafile):
        return None,None
    uadata = pd.read_parquet(rmsuafile, columns=cols)
    # handle any database pollution
    uadata = uadata[uadata['Y']==int(year)]

    uadata = uadata.assign(ts = pd.to_datetime(uadata['Dtstamp'], unit='s', utc=True))
    uadata['LocalTime'] = [ts.strftime('%Y%m%d_%H%M%S') for ts in uadata.ts]

    # create image filename
    uadata['fn']=[f'/img/single/{y}/{y}{m:02d}/'+f.replace('.fits','.jpg') 
        for f,y,m in zip(uadata.Filename, uadata.Y, uadata.M)]

    print(datetime.datetime.now(), 'checking target urls exist')
    uadata['targfn'] = [checkUrl(s3, x) for x in uadata.fn]
    print(datetime.datetime.now(), 'done')

    # create array for source
    print(datetime.datetime.now(), 'add source column')
    srcs = ['2Single']*len(uadata.Filename)

    #eventtime,source,shower,Mag,loccam,url,imgs

    # and put it all in a dataframe
    print(datetime.datetime.now(), 'create interim dataframe')
    hdr=['eventtime','source','shower','Mag','loccam','url','imgs', 'loctime', 'Y','M']
    resdf = pd.DataFrame(zip(uadata.Dtstamp, srcs, uadata.Shwr, 
        uadata.Mag, uadata.ID, uadata.targfn, uadata.targfn, uadata.LocalTime,
        uadata.Y, uadata.M), columns=hdr)

    # fix up some mangled historical data
    resdf.loc[resdf.loccam=='Ringwood_N_UK000S', 'loccam'] = 'UK000S'
    resdf.loc[resdf.loccam=='Tackley_SW_UK0006', 'loccam'] = 'UK0006'

    if newonly is True:
        return resdf, rmsuafile
    else:
        return resdf, None


def convertMatchToSrchable(datadir, year, newonly=True):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    print(datetime.datetime.now(), 'reading merged match file')
    if newonly is False:
        infile = os.path.join(datadir, 'matched', f'matches-full-{year}.parquet.snap')
    else:
        infile = os.path.join(datadir, 'searchidx', f'matches-full-{year}-new.parquet.snap')
    cols = ['dtstamp','src','_stream','_mag','stations','url','img', '_Y_ut']
    if not os.path.isfile(infile):
        return None,None
    newm = pd.read_parquet(infile, columns=cols)
    newm = newm[newm['_Y_ut']==int(year)] 
    outdf = pd.concat([newm['dtstamp'], newm['src'], newm['_stream'], newm['_mag'], newm['stations'], newm['url'], newm['img']], 
        axis=1, keys=['eventtime','source','shower','Mag','loccam','url','imgs'])
    if newonly is True:
        return outdf, infile
    else:
        return outdf, None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python createSearchableFormat.py year mode outdir')
        exit(1)
    else:
        datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))

        year = sys.argv[1]
        mode = sys.argv[2]
        outdir = os.path.join(datadir, 'searchidx')
        if len(sys.argv) > 3:
            outdir = sys.argv[3]

        # create a set of single-station data and merge with last match set
        if mode == 'singles':
            print(datetime.datetime.now(), 'converting single-station data')
            newsingles, fname = convertSingletoSrchable(datadir, year, True)
            outfile = os.path.join(outdir, '{:s}-singles-new.csv'.format(year))
            if newsingles is not None: 
                newsingles.to_csv(outfile, index=False, header=False)
            if fname is not None:
                os.remove(fname)

        # create a set of matched data and merge with last single-station set
        elif mode == 'matches':
            print(datetime.datetime.now(), 'converting match data')
            newmatches, fname = convertMatchToSrchable(datadir, year, True)
            outfile = os.path.join(outdir, '{:s}-matches-new.csv'.format(year))
            if newmatches is not None: 
                newmatches.to_csv(outfile, index=False, header=False)
            if fname is not None:
                os.remove(fname)
        
        else:
            print('usage: createSearchableFormat year mode outdir')
