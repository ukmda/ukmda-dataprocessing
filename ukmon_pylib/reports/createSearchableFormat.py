#
# python module to read data in various formats and create a format that can be searched
# with S3 SQL statements from a lambda function. The lambda is invoked from a REST API
# via the Search page on the website. 
#

import sys
import os
import pandas as pd
import datetime 


def convertSingletoSrchable(datadir, year, outdir, weburl):
    print(datetime.datetime.now(), 'single-detection searchable index start')

    # load the single-station combined data
    rmsuafile = os.path.join(datadir, 'single', 'singles-{}.parquet.gzip'.format(year))
    print(datetime.datetime.now(), f'read single file to get shower and mag: {rmsuafile}')
    uadata = pd.read_parquet(rmsuafile)    

    uadata = uadata.assign(ts = pd.to_datetime(uadata['Dtstamp'], unit='s', utc=True))
    uadata['LocalTime'] = [ts.strftime('%Y%m%d_%H%M%S') for ts in uadata.ts]

    # create image filename
    uadata['fn']=[f'{weburl}/img/single/{y}/{y}{m:02d}/'+f.replace('.fits','.jpg') 
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
    ufodata['url']=[f'{weburl}/img/single/{y}/{y}{m:02d}/M{lt}_{f}P.jpg'
        for f,y,m,lt in zip(ufodata.loccam, ufodata.Y, ufodata.M, ufodata.loctime)]
    ufodata['imgs'] = ufodata.url
    ufodata = ufodata.drop(columns=['loctime','Y','M'])

    # annoying special case for UK0001, H and S which do not upload JPGs
    rmsdata.loc[rmsdata.loccam=='UK0001','url']=f'{weburl}/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK0001','imgs']=f'{weburl}/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000H','url']=f'{weburl}/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000H','imgs']=f'{weburl}/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000S','url']=f'{weburl}/img/missing-white.png'
    rmsdata.loc[rmsdata.loccam=='UK000S','imgs']=f'{weburl}/img/missing-white.png'
    
    resdf = pd.concat([rmsdata,ufodata])

    #print(datetime.datetime.now(), 'save data')
    #outfile = os.path.join(outdir, '{:s}-singleevents.csv'.format(year))
    #resdf.to_csv(outfile, sep=',', index=False)
    #print(datetime.datetime.now(), 'single-detection index created')
    return resdf


def convertMatchToSrchable(config, year, outdir, weburl):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    print('reading merged match file')
    infile = os.path.join(datadir, 'matched', 'matches-full-{}.parquet.gzip'.format(year))
    newm = pd.read_parquet(infile)

    outdf = pd.concat([newm['dtstamp'], newm['src'], newm['_stream'], newm['_mag'], newm['stations'], newm['url'], newm['img']], 
        axis=1, keys=['eventtime','source','shower','Mag','loccam','url','imgs'])
    #print('saving file')
    #outfile = os.path.join(outdir, '{:s}-matchedevents.csv'.format(year))
    #outdf.to_csv(outfile, index=False)
    return outdf


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python createSearchableFormat.py year dest')
        exit(1)
    else:
        datadir = os.getenv('DATADIR')
        weburl = os.getenv('SITEURL')

        year =sys.argv[1]

        fulldf = convertSingletoSrchable(datadir, year, sys.argv[2], weburl)
        if int(year) > 2019:
            mtchdf = convertMatchToSrchable(datadir, year, sys.argv[2], weburl)
            fulldf = pd.concat([fulldf, mtchdf])
        outfile = os.path.join(sys.argv[2], '{:s}-allevents.csv'.format(year))
        fulldf.to_csv(outfile, index=False)
        outfilepq = os.path.join(sys.argv[2], '{:s}-allevents.parquet.gzip'.format(year))
        fulldf.to_parquet(outfilepq, compression='gzip')
        print('file saved')
