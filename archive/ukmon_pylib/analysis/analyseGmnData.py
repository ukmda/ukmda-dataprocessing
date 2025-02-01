# simple scripts to analyse the GMN data in python

import pandas as pd
import os

from converters.gmnTxtToPandas import dirpath


def findDuplicates(yr, mth=None):
    if mth:
        datafile = os.path.join(dirpath, 'parquet', 'monthly', f'gmn_{yr:04d}{mth:02d}.parquet.snap')
    else:
        datafile = os.path.join(dirpath, 'parquet', f'gmn_{yr:04d}.parquet.snap')
    df = pd.read_parquet(datafile)
    df['dupe']=df.duplicated(subset=['id'])
    dupeids = df[df.dupe].sort_values(by=['id']).id
    duperows = df[df.id.isin(dupeids)]
    print(duperows)
    print(len(df))
    return duperows
