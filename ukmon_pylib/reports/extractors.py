#
# Various sorts of extract from the raw data
#
# 
import os 
import sys
import pandas as pd
from fileformats import imoWorkingShowerList as imo
import datetime


def createSplitMatchFile(yr, mth=None, shwr=None, matches=None):
    """ creates the UFO-orbit compatible matches file for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    datadir = os.getenv('DATADIR')
    if matches is None:
        infname = os.path.join(datadir, 'matched',f'matches-full-{yr}.parquet.gzip')
        if not os.path.isfile(infname):
            return 
        matches=pd.read_parquet(infname)

    ofname = os.path.join(datadir, 'matched',f'matches-{yr}.csv')
    if mth is not None:
        locmatches = matches[matches._M_ut == mth]
        os.makedirs(os.path.join(datadir, 'browse','monthly'),exist_ok=True)
        ofname = os.path.join(datadir, 'browse','monthly',f'{yr}{mth:02d}-matches.csv')
    if shwr is not None:
        locmatches = matches[matches._stream == shwr]
        os.makedirs(os.path.join(datadir, 'browse','showers'),exist_ok=True)
        ofname = os.path.join(datadir, 'browse','showers',f'{yr}-{shwr}-matches.csv')

    locmatches = locmatches.sort_values(by=['_D_ut','_h_ut','_mi_ut','_s_ut'])
    truncmatch=locmatches.drop(columns=['dtstamp','orbname','src','url','img',
        '# date','mjd','id','iau','name','mass','pi','Q','true_anom','EA',
        'MA','Tj','T','last_peri','jacchia1','Jacchia2','numstats','stations'])

    if len(truncmatch) > 0:
        truncmatch.to_csv(ofname, index=False)
    return 


def createUFOSingleMonthlyExtract(yr, mth=None, shwr=None, dta=None):
    """ creates the UFO single-station data for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    print('ufo singles file')
    datadir = os.getenv('DATADIR')
    if dta is None:
        fname = os.path.join(datadir, 'consolidated','M_{}-unified.csv'.format(yr))
        if not os.path.isfile(fname):
            return 
        dta = pd.read_csv(fname, skipinitialspace=True)

    if mth is not None:
        locdta = dta[dta['M(UT)']==mth]
        os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
        locdta = locdta.sort_values(by=['LocalTime','Group'])
        if len(locdta) > 0:
            locdta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{}{:02d}-detections-ufo.csv'.format(yr, mth)), index=False)
    elif shwr is not None:
        if shwr != 'spo':
            locdta = dta[dta['Group']=='J8_'+shwr]
        else:
            locdta = dta[dta['Group']==shwr]
        os.makedirs(os.path.join(datadir, 'browse', 'showers'), exist_ok=True)
        locdta = locdta.sort_values(by=['LocalTime','Group'])
        if len(locdta) > 0:
            locdta.to_csv(os.path.join(datadir, 'browse', 'showers', '{}-{}-detections-ufo.csv'.format(yr, shwr)), index=False)

    return 


def createRMSSingleMonthlyExtract(yr, mth=None, shwr=None, dta=None, withshower=False):
    """ creates the RMS single-station data for sharing through the website.
        Note target location is hardcoded. 
    Args:
        year (int): the year to process
        mth (int): optional month. If provided, the data will be filtered 
        shwr (string): optional shower code. If provided, the data will be filtered 
        
    """
    #print(f'rms singles file, withshower {withshower}')
    datadir = os.getenv('DATADIR')
    if dta is None:
        fname = os.path.join(datadir, 'single','singles-{}.parquet.gzip'.format(yr))
        if not os.path.isfile(fname):
            return 
        dta = pd.read_parquet(fname)

    #locdta = dta[dta.ID.str.contains('UK0')]
    if mth is not None:
        locdta = dta[dta['M']==mth]
        os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
        locdta = locdta.sort_values(by=['D','h','mi','s'])
        if withshower is True:
            locdta=locdta.drop(columns=['AngVel','Filename','Dtstamp'])
        else:
            locdta=locdta.drop(columns=['AngVel','Shwr','Filename','Dtstamp'])
        locdta.Ver='R91'
        if len(locdta) > 0:
            if withshower is True:
                locdta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{}{:02d}-rms-shwr.csv'.format(yr, mth)), index=False)
            else:
                locdta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{}{:02d}-detections-rms.csv'.format(yr, mth)), index=False)
    elif shwr is not None:
        locdta = dta[dta['Shwr']==shwr]
        os.makedirs(os.path.join(datadir, 'browse', 'showers'), exist_ok=True)
        locdta = locdta.sort_values(by=['D','h','mi','s'])
        if withshower is True:
            locdta=locdta.drop(columns=['AngVel','Filename','Dtstamp'])
        else:
            locdta=locdta.drop(columns=['AngVel','Shwr','Filename','Dtstamp'])
        locdta.Ver='R91'
        if len(locdta) > 0:
            if withshower is True:
                locdta.to_csv(os.path.join(datadir, 'browse', 'showers', '{}-{}-rms-shwr.csv'.format(yr, shwr)), index=False)
            else:
                locdta.to_csv(os.path.join(datadir, 'browse', 'showers', '{}-{}-detections-rms.csv'.format(yr, shwr)), index=False)

    return 


def extractAllShowersData(ymd):
    print('getting shower data')
    sl = imo.IMOshowerList()
    showerlist = sl.getMajorShowers(True, True).strip().split(' ')

    yr = str(ymd)[:4]
    currdt = None
    if ymd > 9999:
        currdt = datetime.datetime.strptime(str(ymd), '%Y%m')
        now = datetime.datetime.now()
        if now.year == currdt.year and now.month == currdt.month:
            currdt = currdt.replace(day = now.day)

    print(f'processing data for {currdt}')
    datadir = os.getenv('DATADIR')
    infname = os.path.join(datadir, 'matched',f'matches-full-{yr}.parquet.gzip')
    if not os.path.isfile(infname):
        print(f'unable to open {infname}')
        return 
    matches=pd.read_parquet(infname)

    for shwr in showerlist:
        doit = True
        if currdt is not None and shwr != 'spo':
            edt = sl.getEnd(shwr) + datetime.timedelta(days=5)
            sdt = sl.getStart(shwr) + datetime.timedelta(days=-5)
            #print(f'{shwr} start {sdt} end {edt}')
            if currdt > edt or currdt < sdt:
                #print('skipping')
                doit = False
        if doit is True:
            print(f'processing matches for {shwr}')
            createSplitMatchFile(yr, shwr=shwr, matches=matches)
    del matches

    fname = os.path.join(datadir, 'consolidated','M_{}-unified.csv'.format(yr))
    if not os.path.isfile(fname):
        print(f'unable to open {fname}')
        return 
    ufosingles = pd.read_csv(fname, skipinitialspace=True)
    fname = os.path.join(datadir, 'single','singles-{}.parquet.gzip'.format(yr))
    if not os.path.isfile(fname):
        print(f'unable to open {fname}')
        return 
    rmssingles = pd.read_parquet(fname)

    for shwr in showerlist:
        doit = True
        if currdt is not None and shwr != 'spo':
            edt = sl.getEnd(shwr) + datetime.timedelta(days=5)
            sdt = sl.getStart(shwr) + datetime.timedelta(days=-5)
            #print(f'{shwr} start {sdt} end {edt}')
            if currdt > edt or currdt < sdt:
                #print('skipping')
                doit = False
        if doit is True:
            print(f'processing RMS singles for {shwr}')
            createRMSSingleMonthlyExtract(yr, shwr=shwr, dta=rmssingles)
            createRMSSingleMonthlyExtract(yr, shwr=shwr, dta=rmssingles, withshower=True)
            print(f'processing UFO singles for {shwr}')
            createUFOSingleMonthlyExtract(yr, shwr=shwr, dta=ufosingles)
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
        print('processing', yr, m)
        createUFOSingleMonthlyExtract(yr, mth=m)
        createRMSSingleMonthlyExtract(yr, mth=m)
        createRMSSingleMonthlyExtract(yr, mth=m, withshower=True)
        createSplitMatchFile(yr, mth=m)
