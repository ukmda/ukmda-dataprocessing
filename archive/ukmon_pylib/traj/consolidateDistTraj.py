# Copyright (C) 2018-2023 Mark McIntyre

import os
import sys
import glob
import datetime

from wmpl.Trajectory.CorrelateDB import ObservationsDatabase, TrajectoryDatabase, CandidateDatabase


def mergeDatabases(srcdir, dbdir, ignore_missing=False, purge_records=False):
    targdb = os.path.join(dbdir, 'observations.db')
    if os.path.isfile(targdb) or ignore_missing:
        obsdb = ObservationsDatabase(dbdir, purge_records=purge_records)
        flist = glob.glob(os.path.join(srcdir, 'observations_*.db'))
        flist.sort()
        for fl in flist:
            tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            print(f'{tstamp} processing {fl}')
            if obsdb.mergeObsDatabase(fl):
                os.remove(fl)
        obsdb.closeObsDatabase()

    targdb = os.path.join(dbdir, 'trajectories.db')
    if os.path.isfile(targdb) or ignore_missing:
        trajdb = TrajectoryDatabase(dbdir, purge_records=purge_records)
        flist = glob.glob(os.path.join(srcdir, 'trajectories_*.db'))
        flist.sort()
        for fl in flist:
            tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            print(f'{tstamp} processing {fl}')
            if trajdb.mergeTrajDatabase(fl):
                os.remove(fl)
        trajdb.closeTrajDatabase()

    # should never need to run this part as the candidates are all made in one place
    targdb = os.path.join(dbdir, 'candidates.db')
    if os.path.isfile(targdb):
        canddb = CandidateDatabase(dbdir)
        flist = glob.glob(os.path.join(srcdir, 'candidates_*.db'))
        flist.sort()
        for fl in flist:
            tstamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            print(f'{tstamp} processing {fl}')
            if canddb.mergeCandDatabase(fl):
                os.remove(fl)
        canddb.closeCandDatabase()

    print('done')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: consolidateDistTraj folder_containing_srcdbs targ_dbdir')
        exit(0)
    srcdir = sys.argv[1]
    dbdir = sys.argv[2]
    mergeDatabases(srcdir, dbdir)
