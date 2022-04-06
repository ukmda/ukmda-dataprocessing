#
# Various sorts of extract from the raw data
#
# 
import os 
import sys
import pandas as pd


def createSplitMatchFile(yr, mth=None, shwr=None):
    """ creates the UFO-orbit compatible matches file for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    datadir = os.getenv('DATADIR')
    infname = os.path.join(datadir, 'matched',f'matches-full-{yr}.parqet.gzip')
    if not os.path.isfile(infname):
        return 

    ofname = os.path.join(datadir, 'matched',f'matches-{yr}.csv')
    matches=pd.read_parquet(infname)
    if mth is not None:
        matches = matches[matches._M_ut == mth]
        os.makedirs(os.path.join(datadir, 'browse','monthly'),exist_ok=True)
        ofname = os.path.join(datadir, 'browse','monthly',f'{yr}{mth:02d}-matches.csv')
    if shwr is not None:
        matches = matches[matches._stream == shwr]
        os.makedirs(os.path.join(datadir, 'browse','showers'),exist_ok=True)
        ofname = os.path.join(datadir, 'browse','showers',f'{yr}-{shwr}-matches.csv')

    matches = matches.sort_values(by=['_D_ut','_h_ut','_mi_ut','_s_ut'])
    truncmatch=matches.drop(columns=['dtstamp','orbname','src','url','img',
        '# date','mjd','id','iau','name','mass','pi','Q','true_anom','EA',
        'MA','Tj','T','last_peri','jacchia1','Jacchia2','numstats','stations'])

    if len(truncmatch) > 0:
        truncmatch.to_csv(ofname, index=False)
    return 


def createUFOSingleMonthlyExtract(yr, mth=None, shwr=None):
    """ creates the UFO single-station data for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    datadir = os.getenv('DATADIR')

    fname = os.path.join(datadir, 'consolidated','M_{}-unified.csv'.format(yr))
    if not os.path.isfile(fname):
        return 

    dta = pd.read_csv(fname, skipinitialspace=True)
    if mth is not None:
        dta = dta[dta['M(UT)']==mth]
        os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
        dta = dta.sort_values(by=['LocalTime','Group'])
        if len(dta) > 0:
            dta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{}{:02d}-detections-ufo.csv'.format(yr, mth)), index=False)
    elif shwr is not None:
        if shwr != 'spo':
            dta = dta[dta['Group']=='J8_'+shwr]
        else:
            dta = dta[dta['Group']==shwr]
        os.makedirs(os.path.join(datadir, 'browse', 'showers'), exist_ok=True)
        dta = dta.sort_values(by=['LocalTime','Group'])
        if len(dta) > 0:
            dta.to_csv(os.path.join(datadir, 'browse', 'showers', '{}-{}-detections-ufo.csv'.format(yr, shwr)), index=False)

    return 


def createRMSSingleMonthlyExtract(yr, mth=None, shwr=None):
    """ creates the RMS single-station data for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    datadir = os.getenv('DATADIR')
    fname = os.path.join(datadir, 'single','singles-{}.parquet.gzip'.format(yr))
    if not os.path.isfile(fname):
        return 

    dta = pd.read_parquet(fname)
    dta = dta[dta.ID.str.contains('UK0')]
    if mth is not None:
        dta = dta[dta['M']==mth]
        os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
        dta = dta.sort_values(by=['D','h','m','s'])
        dta=dta.drop(columns=['AngVel','Shwr','Filename','Dtstamp'])
        dta.Ver='R91'
        if len(dta) > 0:
            dta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{}{:02d}-detections-rms.csv'.format(yr, mth)), index=False)
    elif shwr is not None:
        dta = dta[dta['Shwr']==shwr]
        os.makedirs(os.path.join(datadir, 'browse', 'showers'), exist_ok=True)
        dta = dta.sort_values(by=['D','h','m','s'])
        dta=dta.drop(columns=['AngVel','Shwr','Filename','Dtstamp'])
        dta.Ver='R91'
        if len(dta) > 0:
            dta.to_csv(os.path.join(datadir, 'browse', 'showers', '{}-{}-detections-rms.csv'.format(yr, shwr)), index=False)

    return 


if __name__ == '__main__':
    # do all three for a range of dates
    if len(sys.argv) < 3:
        print('usage: python extractors.py yyyy mm optional-nummonths')
        exit(0)

    yr = int(sys.argv[1])
    mth = int(sys.argv[2])
    tomth = mth+1
    if len(sys.argv) > 3:
        tomth = mth + int(sys.argv[3])

    for m in range(mth, tomth):
        print('processing', yr, mth)
        createUFOSingleMonthlyExtract(yr, mth=m)
        createRMSSingleMonthlyExtract(yr, mth=m)
        createSplitMatchFile(yr, mth=m)
