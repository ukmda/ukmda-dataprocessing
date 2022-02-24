# convert a csv file to parquet format

import sys
import pandas as pd
import os

df = pd.read_csv(sys.argv[1])

fn, _ = os.path.splitext(sys.argv[1])

df = df.rename(columns={'m':'mi'})
df = df.rename(columns={'_m_ut':'_mi_ut'})

df.to_parquet(fn + '.parquet.gzip', compression='gzip')
