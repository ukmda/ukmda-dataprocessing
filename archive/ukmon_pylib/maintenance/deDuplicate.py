# copyright (c) Mark McIntyre 

import pandas as pd
import shutil
import sys
import os


def deduplicateUFO(fname):
    shutil.copyfile(fname, f'{fname}.bkp')
    df = pd.read_csv(fname)
    orig_count = len(df)
    df = df.drop_duplicates(subset=['Group','LocalTime','Mag','Dur(sec)','Loc_Cam'])
    df.to_csv(fname)
    new_count = len(df)
    print(f'{fname}: was {orig_count} now {new_count}')


def deduplicateRMS(fname):
    shutil.copyfile(fname, f'{fname}.bkp')
    df = pd.read_csv(fname)
    orig_count = len(df)
    df = df.drop_duplicates()
    df.to_csv(fname)
    new_count = len(df)
    print(f'{fname}: was {orig_count} now {new_count}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python deDuplicate.py UFOfiletodedupe')
    else:
        fname = sys.argv[1]
        if not os.path.isfile(fname):
            print(f'{sys.argv[1]} not found')
        else:
            if fname[0] == 'M':
                deduplicateUFO(fname)
            else:
                deduplicateRMS(fname)

