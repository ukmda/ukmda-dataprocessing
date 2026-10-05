"""
copyright Mark McIntyre, 2026-

Compare two trajectory databases for discrepancies. Useful when testing. 

"""

import pandas as pd
import os
import sys
import datetime
import argparse

from wmpl.Utils.Pickling import loadPickle
from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced
from wmpl.Utils.TrajConversions import datetime2JD


def compareTrajDbs(db1, db2, maxerr=1, outdir=None):
    src1dir, db1name = os.path.split(db1)
    src2dir, db2name = os.path.split(db2)

    sqlstr = f'select jdt_ref, participating_stations from trajectories;'

    tdb1 = TrajectoryDatabase(src1dir, db_name=db1name)
    trajs = tdb1.dbhandle.execute(sqlstr).fetchall()
    old = pd.DataFrame(trajs, columns=['jdt_ref','stations'])
    old.sort_values(by='jdt_ref', inplace=True)
    print(f'db1 date range {old.iloc[0].jdt_ref} {old.iloc[-1].jdt_ref}')

    tdb2 = TrajectoryDatabase(src2dir, db_name=db2name)
    trajs = tdb2.dbhandle.execute(sqlstr).fetchall()
    new = pd.DataFrame(trajs, columns=['jdt_ref','stations'])
    new.sort_values(by='jdt_ref', inplace=True)
    print(f'db2 date range {new.iloc[0].jdt_ref} {new.iloc[-1].jdt_ref}')

    olddiffs = old.copy()
    newdiffs = new.copy()
    maxerr = maxerr/86400 # convert to days

    for _, rw in new.iterrows():
        jdt_ref = rw.jdt_ref
        stats = rw.stations
        tmpdf = olddiffs[abs(olddiffs.jdt_ref-jdt_ref) < maxerr]
        if len(tmpdf) > 0:
            tmpdf2 = tmpdf[tmpdf.stations==stats]
            if len(tmpdf2) > 0:
                olddiffs.drop(index=tmpdf.index, inplace=True)
            continue

    for _, rw in old.iterrows():
        jdt_ref = rw.jdt_ref
        stats = rw.stations
        tmpdf = newdiffs[abs(newdiffs.jdt_ref-jdt_ref) < maxerr]
        if len(tmpdf) > 0:
            tmpdf2 = tmpdf[tmpdf.stations==stats]
            if len(tmpdf2) > 0:
                newdiffs.drop(index=tmpdf.index, inplace=True)
            continue

    print(f'new {len(new)} vs gmn {len(old)}')
    print(f'max time tolerance {maxerr*86400} secs')
    print(f'{len(newdiffs)} differences left in new')
    print(f'{len(olddiffs)} differences left in old')
    if outdir is not None:
        olddiffs.to_csv(os.path.join(outdir, f'olddiffs.csv'), index=False)
        newdiffs.to_csv(os.path.join(outdir, f'newdiffs.csv'), index=False)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Compare two trajectory SQlite databases')
    arg_parser.add_argument('db1_path', metavar='DB1_PATH', type=str,  help='First database')
    arg_parser.add_argument('db2_path', metavar='DB2_PATH', type=str,  help='Second database')
    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', type=str, help='Where to save results to, default is current folder', default='.')
    arg_parser.add_argument('-m', '--maxerr', metavar='MAXERR', type=float, help='max difference to allow', default=0.5)
    cml_args = arg_parser.parse_args()

    print(f'reading {cml_args.db1_path} and {cml_args.db2_path}, saving to {cml_args.outdir}, max err {cml_args.maxerr}')    

    compareTrajDbs(cml_args.db1_path, cml_args.db2_path, maxerr=cml_args.maxerr, outdir=cml_args.outdir)
