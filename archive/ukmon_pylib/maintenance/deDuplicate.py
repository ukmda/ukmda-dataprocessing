# copyright (c) Mark McIntyre 

import pandas as pd
import shutil
import sys
import os
import argparse


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
    arg_parser = argparse.ArgumentParser(description='Deduplicate source data')
    arg_parser.add_argument('srcfile', metavar='SRCFILE', type=str, help='source file to read in')
    cml_args = arg_parser.parse_args()

    fname = cml_args.srcfile
    if not os.path.isfile(fname):
        print(f'{cml_args.srcfile} not found')
    else:
        if fname[0] == 'M':
            deduplicateUFO(fname)
        else:
            deduplicateRMS(fname)

