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


def convertSingletoSrchable(datadir, year, newonly=True):
    print(datetime.datetime.now(), 'single-detection searchable index start')

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

    # create array for source
    print(datetime.datetime.now(), 'add source column')
    srcs = ['2Single']*len(uadata.Filename)

    #eventtime,source,shower,Mag,loccam,url,imgs

    # and put it all in a dataframe
    print(datetime.datetime.now(), 'create interim dataframe')
    hdr=['eventtime','source','shower','Mag','loccam','url','imgs', 'loctime', 'Y','M']
    resdf = pd.DataFrame(zip(uadata.Dtstamp, srcs, uadata.Shwr, 
        uadata.Mag, uadata.ID, uadata.fn, uadata.fn, uadata.LocalTime,
        uadata.Y, uadata.M), columns=hdr)

    # fix up some mangled historical data
    resdf.loc[resdf.loccam=='Ringwood_N_UK000S', 'loccam'] = 'UK000S'
    resdf.loc[resdf.loccam=='Tackley_SW_UK0006', 'loccam'] = 'UK0006'

    # select the RMS data out, its good now
    # FIXME - needs to select for "not FF_UK9" so we can include non-UK cameras
    rmsdata=resdf[resdf.url.str.contains('FF_UK0')]
    rmsdata = rmsdata.drop(columns=['Y','M','loctime'])

    # now select out the UFO dta and fix it up
    ufodata=resdf[resdf.url.str.contains('FF_UK9')]
    #fix up Clanfield cameras
    ufodata.loc[ufodata.loccam=='UK9990', 'loccam'] = 'Clanfield_NE'
    ufodata.loc[ufodata.loccam=='UK9989', 'loccam'] = 'Clanfield_NW'
    ufodata.loc[ufodata.loccam=='UK9988', 'loccam'] = 'Clanfield_SE'
    ufodata = ufodata.drop(columns=['url','imgs'])

    # create the URL and imgs fields
    ufodata['url']=[f'/img/single/{y}/{y}{m:02d}/M{lt}_{f}P.jpg'
        for f,y,m,lt in zip(ufodata.loccam, ufodata.Y, ufodata.M, ufodata.loctime)]
    ufodata['imgs'] = ufodata.url
    ufodata = ufodata.drop(columns=['loctime','Y','M'])

    # annoying special case for UK0001, H and S which do not upload JPGs
    rmsdata.loc[rmsdata.loccam=='UK0001','url']='/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK0001','imgs']='/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000H','url']='/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000H','imgs']='/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000S','url']='/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000S','imgs']='/img/missing-white.png'
    
    resdf = pd.concat([rmsdata,ufodata])
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
        print('usage: python createSearchableFormat.py year dest mode')
        exit(1)
    else:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')

        year = sys.argv[1]
        mode = sys.argv[2]

        # create a set of single-station data and merge with last match set
        if mode == 'singles':
            print(datetime.datetime.now(), 'converting single-station data')
            newsingles, fname = convertSingletoSrchable(datadir, year, True)
            outfile = os.path.join(datadir, 'searchidx', '{:s}-singles-new.csv'.format(year))
            if newsingles is not None: 
                newsingles.to_csv(outfile, index=False, header=False)
            if fname is not None:
                os.remove(fname)

        # create a set of matched data and merge with last single-station set
        elif mode == 'matches':
            print(datetime.datetime.now(), 'converting match data')
            newmatches, fname = convertMatchToSrchable(datadir, year, True)
            outfile = os.path.join(datadir, 'searchidx', '{:s}-matches-new.csv'.format(year))
            if newmatches is not None: 
                newmatches.to_csv(outfile, index=False, header=False)
            if fname is not None:
                os.remove(fname)
        
        else:
            print('usage: createSearchableFormat yyyy matches_or_singles')
