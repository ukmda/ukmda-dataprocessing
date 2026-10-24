# convert a csv file to parquet format
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import pandas as pd
import os
import argparse

arg_parser = argparse.ArgumentParser(description='Convert a WMPL trajectory_summary.txt file into a Pandas parquet file')
arg_parser.add_argument('csvfile', metavar='CSVFILE', type=str, help='source file to read in')
cml_args = arg_parser.parse_args()

df = pd.read_csv(cml_args.csvfile, skipinitialspace=True)

fn, _ = os.path.splitext(cml_args.csvfile)

# rename columns to be unique
df = df.rename(columns={'m':'mi'})
df = df.rename(columns={'_m_ut':'_mi_ut'})

if 'match' in fn:
    # fill in any #NAs in the mjd column
    df.fillna({'mjd': df._mjd}, inplace=True)
    if 'traj_id' in df.columns:
        df.fillna({'traj_id':'n/a'}, inplace=True)
if 'single' in fn:
    df = df.drop_duplicates()


df.to_parquet(fn + '.parquet.snap', compression='snappy')
