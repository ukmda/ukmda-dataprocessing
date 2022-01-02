#
# Various sorts of extract from the raw data
#
# 
import datetime
import os 
import sys
import pandas as pd
from dateutil.relativedelta import relativedelta
from fileformats import UAFormats as uaf 


def createUFOSingleMonthlyExtract(yr, mth):
    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    sd = datetime.datetime(yr, mth, 1)
    ed = sd + relativedelta(months=1)
    dsv = uaf.DetectedCsv(os.path.join(datadir, 'consolidated','M_{}-unified.csv'.format(yr)))
    if dsv.rawdata is not None:
        dta = dsv.selectByDateRange(sd, ed)
        os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
        dta = dta.sort_values(by=['LocalTime','Group'])
        dta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{:04d}{:02d}-detections-ufo.csv'.format(yr, mth)), index=False)
    return 


def createRMSSingleMonthlyExtract(yr, mth):
    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    fname = os.path.join(datadir, 'consolidated','P_{}-unified.csv'.format(yr))
    if not os.path.isfile(fname):
        print('datafile missing!')
        return 
    dsv = pd.read_csv(fname,index_col=False)
    dsv = dsv[dsv.Y == yr]
    dta = dsv[dsv.M == mth]
    os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
    dta = dta.sort_values(by=['D','h','m','s'])
    dta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{:04d}{:02d}-detections-rms.csv'.format(yr, mth)), index=False)
    return 


def createMatchedMonthlyExtract(yr, mth):
    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    fname = os.path.join(datadir, 'matched','matches-{}.csv'.format(yr))
    if not os.path.isfile(fname):
        print('datafile missing!')
        return 
    dsv = pd.read_csv(fname,index_col=False)
    dsv = dsv[dsv._Y_ut == yr]
    dta = dsv[dsv._M_ut == mth]
    os.makedirs(os.path.join(datadir, 'browse', 'monthly'), exist_ok=True)
    dta = dta.sort_values(by=['_D_ut','_h_ut','_m_ut','_s_ut'])
    dta.to_csv(os.path.join(datadir, 'browse', 'monthly', '{:04d}{:02d}-matches.csv'.format(yr, mth)), index=False)
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
        createUFOSingleMonthlyExtract(yr, m)
        createRMSSingleMonthlyExtract(yr, m)
        createMatchedMonthlyExtract(yr, m)
