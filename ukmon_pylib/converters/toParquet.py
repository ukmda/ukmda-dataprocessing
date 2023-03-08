# convert a csv file to parquet format
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import pandas as pd
import os

df = pd.read_csv(sys.argv[1], skipinitialspace=True)

fn, _ = os.path.splitext(sys.argv[1])

# rename columns to be unique
df = df.rename(columns={'m':'mi'})
df = df.rename(columns={'_m_ut':'_mi_ut'})

if 'match' in fn:
    # fill in any #NAs in the mjd column
    df.mjd.fillna(df._mjd, inplace=True)
if 'single' in fn:
    df = df.drop_duplicates()

df.to_parquet(fn + '.parquet.snap', compression='snappy')
