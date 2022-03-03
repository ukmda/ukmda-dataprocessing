#
# python module to merge the matches-yyyy and matches-extras-yyyy files. 
# Aside: i need to do away with this and create the full file from scratch 
#

import os
import sys
import pandas as pd
import datetime 

from wmplloc.Math import jd2Date


def createMergedMatchFile(datadir, year, weburl):
    """ Convert matched data records to searchable format

    Args:
        configfile (str): name of the local config file
        year (int): the year to process
        outdir (str): where to save the file
        
    """
    weburl = weburl + '/reports/' + year + '/orbits/'

    matchfile = os.path.join(datadir, 'matched', 'matches-{}.csv'.format(year))
    extrafile = os.path.join(datadir, 'matched', 'matches-extras-{}.csv'.format(year))
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

    mtch['idxcol'] = mtch._mjd
    xtra['idxcol'] = xtra.mjd

    mtch = mtch.set_index(['idxcol'])
    xtra = xtra.set_index(['idxcol'])
    newm = mtch.join(xtra)
    newm = newm.drop_duplicates(subset=['_mjd','_sol','_ID1','_ra_o','_dc_o','_amag','_ra_t','_dc_t'])

    outfile = os.path.join(datadir, 'matched', 'matches-full-{}.csv'.format(year))
    newm.to_csv(outfile, index=False)

    return newm


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python mergeMatchFiles.py year dest')
        exit(1)
    else:
        datadir = os.getenv('DATADIR')
        weburl = os.getenv('SITEURL')

        year = sys.argv[1]

    createMergedMatchFile(datadir, year, weburl)
