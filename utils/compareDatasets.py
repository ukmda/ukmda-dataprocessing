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



def getDifferent(dtval, datadir='.', outdir='.', maxerr=0.001):
    old = pd.read_csv(os.path.join(datadir, f'old_{dtval}.txt'), names=['traj'])
    new = pd.read_csv(os.path.join(datadir, f'new_{dtval}.txt'), names=['traj'])

    old['timeval']=[float(x[9:19]) for x in old.traj]
    new['timeval']=[float(x[9:19]) for x in new.traj]

    old['ctry'] = ['_'.join(sorted(x[20:].split('_'))) for x in old.traj]
    new['ctry'] = [x[20:] for x in new.traj]

    olddiffs = old.copy()
    newdiffs = new.copy()

    for _, rw in new.iterrows():
        traj = rw.traj
        ctry = rw.ctry
        timeval = rw.timeval
        tmpdf = olddiffs[olddiffs.traj == traj]
        if len(tmpdf) > 0:
            olddiffs.drop(index=tmpdf.index, inplace=True)
            continue
        tmpdf = olddiffs[olddiffs.ctry==ctry]
        if len(tmpdf) > 0:
            tmpdf = tmpdf[abs(tmpdf.timeval-timeval) < maxerr]
            if len(tmpdf) > 0:
                olddiffs.drop(index=tmpdf.index, inplace=True)
                continue

    for _, rw in old.iterrows():
        traj = rw.traj
        ctry = rw.ctry
        timeval = rw.timeval
        tmpdf = newdiffs[newdiffs.traj == traj]
        if len(tmpdf) > 0:
            newdiffs.drop(index=tmpdf.index, inplace=True)
            continue
        tmpdf = newdiffs[newdiffs.ctry==ctry]
        if len(tmpdf) > 0:
            tmpdf = tmpdf[abs(tmpdf.timeval-timeval) < maxerr]
            if len(tmpdf) > 0:
                newdiffs.drop(index=tmpdf.index, inplace=True)
                continue

    if outdir is not None:
        olddiffs.to_csv(os.path.join(outdir, f'olddiffs_{dtval}.csv'), index=False)
        newdiffs.to_csv(os.path.join(outdir, f'newdiffs_{dtval}.csv'), index=False)
    return len(old), len(new), olddiffs, newdiffs


def compareOldNewDiffs(dtval, datadir, old=None, new=None, outdir='.'):
    if old is None or new is None:
        old = pd.read_csv(os.path.join(datadir, f'olddiffs_{dtval}.csv'))
        new = pd.read_csv(os.path.join(datadir, f'newdiffs_{dtval}.csv'))

    new['trajdets'] = [getTrajDets(x, True) for x in new.traj]
    new['matched'] =[False] * len(new)
    old['trajdets'] = [getTrajDets(x, False) for x in old.traj]
    old['matched'] =[False] * len(old)
    newdiffs = new.copy()
    for idx, rw in new.iterrows():
        old['ismatched'] = [testIfIn(rw.trajdets, y) for y in old.trajdets]
        if any(old.ismatched):
            newdiffs.at[idx, 'matched'] = True
            old.loc[old.ismatched == True, ['matched']]=True
        
    olddiffs = old.copy()
    for idx, rw in old.iterrows():
        newdiffs['ismatched'] = [testIfIn(rw.trajdets, y) for y in newdiffs.trajdets]
        if any(newdiffs.ismatched):
            olddiffs.at[idx, 'matched'] = True
            newdiffs.loc[newdiffs.ismatched == True, ['matched']]=True
        
    
    olddiffs[olddiffs.matched != True].to_csv(os.path.join(outdir, f'olddiffs_{dtval}.csv'), index=False)
    newdiffs[newdiffs.matched != True].to_csv(os.path.join(outdir, f'newdiffs_{dtval}.csv'), index=False)
    return newdiffs, olddiffs


def testIfIn(idvals, testvals):
    count = 0
    for idval in idvals:
        if idval in testvals:
            count += 1
    if count > 1:
        return True
    return False


def getTrajDets(traj, new=True):
    if new:
        picklepath = os.path.expanduser(f'~/data/trajectories/{traj[:4]}/{traj[:6]}/{traj[:8]}/{traj}')
    else:
        picklepath = f'/srv/meteor/rms/gmn/extracted_data/trajectories/{traj[:4]}/{traj[:6]}/{traj[:8]}/{traj}'
    picklefile = f'{traj[:15]}_trajectory.pickle'
    #print(picklepath, picklefile)
    if os.path.isfile(os.path.join(picklepath, picklefile)):
        newtraj = loadPickle(picklepath, picklefile)
        stns = [obs.station_id for obs in newtraj.observations if obs.ignore_station is False]
        obsdts = [round(obs.jdt_ref*86400 + obs.time_data[0], 2) for obs in newtraj.observations if obs.ignore_station is False]
        idlist = [f'{s}_{j}' for s,j in zip(stns,obsdts)]
        return idlist
    else:
        return []


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Compare two trajectory SQlite databases')
    arg_parser.add_argument('db1_path', metavar='DB1_PATH', type=str,  help='First database')
    arg_parser.add_argument('db2_path', metavar='DB2_PATH', type=str,  help='Second database')
    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', type=str, help='Where to save results to, default is current folder', default='.')
    arg_parser.add_argument('-m', '--maxerr', metavar='MAXERR', type=float, help='max difference to allow', default=0.5)
    cml_args = arg_parser.parse_args()

    print(f'reading {cml_args.db1_path} and {cml_args.db2_path}, saving to {cml_args.outdir}, max err {cml_args.maxerr}')    

    compareTrajDbs(cml_args.db1_path, cml_args.db2_path, maxerr=cml_args.maxerr, outdir=cml_args.outdir)

    #old, new, olddiffs, newdiffs = getDifferent(cml_args.db1_path, cml_args.db2_path, None, cml_args.maxerr)
    #compareOldNewDiffs(cml_args.db1_path, cml_args.db2_path, old=olddiffs, new=newdiffs, outdir=cml_args.outdir)
    #print(f'{old}, {new}, {len(olddiffs)}, {len(newdiffs)}')
