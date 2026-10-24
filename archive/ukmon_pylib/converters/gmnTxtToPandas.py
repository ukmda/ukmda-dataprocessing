# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
import numpy as np
import os
import argparse


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
    df['iau_no'] = df.iau_no.astype(int)
    for c in range(5,82):
        try:
            df[colhdrs[c]] = df[colhdrs[c]].astype(float)
        except Exception:
            print('failed for',colhdrs[c])
    df['BegIn'] = df.BegIn.astype(bool)
    df['EndIn'] = df.EndIn.astype(bool)
    df['NumStat'] = df.NumStat.astype(int)
    return df


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Convert a WMPL trajectory_summary.txt file into a Pandas parquet file')
    arg_parser.add_argument('reportname', metavar='REPORTNAME', type=str, help='source file to read in')
    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', type=str, 
                            help='Where to save the output. Default is the folder containing the source file.')
    arg_parser.add_argument('-r', '--outname', metavar='OUTNAME', type=str, 
                            help='Name to use for the output file. Default is based on the date range of the data.')
    
    cml_args = arg_parser.parse_args()
    print(f' reading from {cml_args.reportname}')
    df = loadOneFile(cml_args.reportname)

    if len(df) == 0:
        print(f'{cml_args.reportname} contained no data')
    else:
        outdir = cml_args.outdir
        if not outdir:
            outdir = os.path.split(cml_args.outname)[0]

        if cml_args.outname:
            # use the provided report name
            repname = f'{cml_args.outname}.parquet.snap'
        else:
            # construct a name from the earliest and latest dates in the file
            sdt = df.iloc[0].utc_beg.strftime('%Y%m')
            edt = df.iloc[0].utc_beg.strftime('%Y%m')
            if sdt == edt:
                repname = f'{sdt}.parquet.snap'
            else:
                repname = f'{sdt}-{edt}.parquet.snap'
        repname = os.path.join(outdir, repname)
        df.to_parquet(repname, index=False)
        print(f'saved to {repname}')
