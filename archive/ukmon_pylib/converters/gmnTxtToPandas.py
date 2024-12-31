# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
import numpy as np
import os
import glob
import sys


colhdrs = ['id','jd_beg','utc_beg','iau_no','iau_code','sollon','lst',
           'RAgeo', 'RAgeosd', 'DECgeo','DECgeosd','LAMgeo','LAMgeosd','BETgeo','BETgeosd','Vgeo','Vgeosd',
           'LAMhel','LAMhelsd','BEThel','BEThelsd','Vhel','Vhelsd',
           'a','asd','e','esd','i','isd','peri','perisd','node','nodesd','pi','pisd','b','bsd','q1','q1sd','f','fsd',
           'M','Msd','Q','Qsd','n','nsd','T','Tsd','Tj','Tjsd','RAapp','RAappsd','DECapp','DECappsd',
           'Azim','Azimsd','Elev','Elevsd','Vinit','Vinitsd','Vavg','Vavgsd',
           'Lat1','Lat1sd','Lon1','Lon1sd','H1','H1sd','Lat2','Lat2sd','Lon2','Lon2sd','H2','H2sd',
           'Dur','Amag','PkHt','F1','mass','Qc','MedianFitErr','BegIn','EndIn','NumStat','stats']


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


def doYear(yr):
    dirpath='F:/videos/MeteorCam/gmndata'
    datafiles = glob.glob(os.path.join(dirpath, f'traj_summary_monthly_{yr}*.txt'))
    for datfile in datafiles:
        newdata = loadOneFile(datfile)
        fn, _ = os.path.splitext(datfile)
        ym = fn[-6:]
        newdata.to_parquet(os.path.join(dirpath, 'parquet', f'gmn_{ym}.parquet.snap'), index=False)


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
