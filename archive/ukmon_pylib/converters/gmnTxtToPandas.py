# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
import numpy as np
import os
import glob
import sys
import datetime


colhdrs = ['id','jd_beg','utc_beg','iau_no','iau_code','sollon','lst',
           'RAgeo', 'RAgeosd', 'DECgeo','DECgeosd','LAMgeo','LAMgeosd','BETgeo','BETgeosd','Vgeo','Vgeosd',
           'LAMhel','LAMhelsd','BEThel','BEThelsd','Vhel','Vhelsd',
           'a','asd','e','esd','i','isd','peri','perisd','node','nodesd','pi','pisd','b','bsd','q1','q1sd','f','fsd',
           'M','Msd','Q','Qsd','n','nsd','T','Tsd','Tj','Tjsd','RAapp','RAappsd','DECapp','DECappsd',
           'Azim','Azimsd','Elev','Elevsd','Vinit','Vinitsd','Vavg','Vavgsd',
           'Lat1','Lat1sd','Lon1','Lon1sd','H1','H1sd','Lat2','Lat2sd','Lon2','Lon2sd','H2','H2sd',
           'Dur','Amag','PkHt','F1','mass','Qc','MedianFitErr','BegIn','EndIn','NumStat','stats']

dirpath='F:/videos/MeteorCam/gmndata'


def loadOneFile(fname):
    print(f'processing {fname}')
    lis = open(fname, 'r').readlines()
    rawdata=[]
    for li in lis: 
        if li[0] == '#' or len(li) < 5:
            continue
        spls = li.split(';')
        convspls=[]
        for spl in spls:
            convspls.append(spl.strip())
        rawdata.append(convspls)          
    df = pd.DataFrame(rawdata, columns = colhdrs)
    df = df.fillna(value=np.nan)
    df['jd_beg'] = df.jd_beg.astype(float)
    df['utc_beg'] = pd.to_datetime(df.utc_beg)
    df['ian_uo'] = df.iau_no.astype(int)
    for c in range(5,82):
        try:
            df[colhdrs[c]] = df[colhdrs[c]].astype(float)
        except Exception:
            print('failed for',colhdrs[c])
    df['BegIn'] = df.BegIn.astype(bool)
    df['EndIn'] = df.EndIn.astype(bool)
    df['NumStat'] = df.NumStat.astype(int)
    return df


def compareTwoFiles(file1, file2):
    df1 = loadOneFile(file1)
    df2 = loadOneFile(file2)

    df1['dupe']=df1.duplicated(subset=['id'])
    print(f'file 1 contains {len(df1[df1.dupe==True].id.unique())} duplicates')
    dupe1 = df1[df1.dupe==True] # noqa: E712
    df1.drop(columns=['dupe'])

    df2['dupe']=df2.duplicated(subset=['id'])
    print(f'file 2 contains {len(df2[df2.dupe==True].id.unique())} duplicates')
    dupe2 = df2[df2.dupe==True] # noqa: E712
    df2.drop(columns=['dupe'])

    mrg = df1.merge(df2.drop_duplicates(), on=['id'], how='left', indicator=True)
    old_not_new = mrg[mrg._merge!='both']
    print(f'there are {len(old_not_new)} rows in the first file not in the second')

    mrg = df2.merge(df1.drop_duplicates(), on=['id'], how='left', indicator=True)
    new_not_old = mrg[mrg._merge!='both']
    print(f'there are {len(new_not_old)} rows in the second file not in the first')

    print(old_not_new)
    old_not_new.to_csv('./old_not_new.csv')
    new_not_old.to_csv('./old_not_new.csv')
    return df1,df2, old_not_new, new_not_old, dupe1, dupe2


def aggregateOneMonth(yr, mth):
    startdt = datetime.datetime(yr, mth, 1) - datetime.timedelta(days=1)
    syr = startdt.year
    smth = startdt.month
    sday = startdt.day
    datafiles = glob.glob(os.path.join(dirpath, 'daily', f'traj_summary_{syr:04d}{smth:02d}{sday:02d}*.txt'))
    prevfile = datafiles[0]
    datafiles = [prevfile] + glob.glob(os.path.join(dirpath, 'daily', f'traj_summary_{yr:04d}{mth:02d}*.txt'))
    mthlydata = None
    for datfile in datafiles:
        newdata = loadOneFile(datfile)
        if mthlydata is None:
            mthlydata = newdata
        else:
            mthlydata = pd.concat([mthlydata, newdata], sort=True)
    mthlydata = mthlydata[mthlydata.utc_beg >= datetime.datetime(yr,mth,1,0,0,0)]
    return mthlydata


def doYear(yr):
    datafiles = glob.glob(os.path.join(dirpath, 'monthly', f'traj_summary_monthly_{yr}*.txt'))
    for datfile in datafiles:
        print(f'processing {datfile}')
        newdata = loadOneFile(datfile)
        fn, _ = os.path.splitext(datfile)
        ym = fn[-6:]
        newdata.to_parquet(os.path.join(dirpath, 'parquet', 'monthly', f'gmn_{ym}.parquet.snap'), index=False)

    datafiles = glob.glob(os.path.join(dirpath, f'traj_summary_yearly_{yr}.txt'))
    for datfile in datafiles:
        print(f'processing {datfile}')
        newdata = loadOneFile(datfile)
        newdata.to_parquet(os.path.join(dirpath, 'parquet', f'gmn_{yr}.parquet.snap'), index=False)
    return


def getStats():
    for yr in range(2022,2025):
        df = pd.read_parquet(f'gmn_{yr}01.parquet.snap')
        for mth in range(2,13):
            try: 
                df2 = pd.read_parquet(f'gmn_{yr}{mth:02d}.parquet.snap')
                df = pd.concat(df, df2)
            except:
                pass
#        df = df[df.Amag < -3.99]
        print(f'{yr}, {len(df)}, {df.Lat1.mean():.1f}, {df.Lat1.max():.1f}, {df.Lat1.min():.1f}, {df.Lat1.std():.1f}')
    print('-----')
    for yr in range(2022,2025):
        df = pd.read_parquet(f'gmn_{yr}01.parquet.snap')
        for mth in range(2,13):
            try: 
                df2 = pd.read_parquet(f'gmn_{yr}{mth:02d}.parquet.snap')
                df = pd.concat(df, df2)
            except:
                pass
        df = df[df.Amag < -3.99]
        print(f'{yr}, {len(df)}, {df.Lat1.mean():.1f}, {df.Lat1.max():.1f}, {df.Lat1.min():.1f}, {df.Lat1.std():.1f}')


if __name__ == '__main__':
    doYear(sys.argv[1])
