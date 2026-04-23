# Copyright (C) 2018-2023 Mark McIntyre

import os
import sys
import glob
import datetime

from wmpl.Trajectory.CorrelateDB import ObservationsDatabase, TrajectoryDatabase, CandidateDatabase
from wmpl.Trajectory.CorrelateRMS import RMSDataHandle
from wmpl.Utils.TrajConversions import jd2Date


def mergeDatabases(srcdir, dbdir, basedir, ignore_missing=False, purge_records=False, matchstart=3):
    """
    merge container databases into the master database, looking for and cleaning deleted trajectories 

    arguments:
        srcdir  location of container databases
        dbdir   location of master databases
        basedir location of raw data and trajectories

    keyword args:
        ignore_missing  default false: if true, create master DBs if not present
        purge_records   default false: if true, purge records from master DBs
        matchstart      default 3: range of days to scan for duplicate and deleted trajectories
    
    """

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

        # get the latest date in the database for use below
        cur = trajdb.dbhandle.execute('select max(jdt_ref) from trajectories where status=1')    
        vals = cur.fetchall()
        jdt_end = float(vals[0][0])
        trajdb.closeTrajDatabase()

    # find and remove duplicates using WMPL's built-in routine to clean up the trajectory DB
    # NB: can only be run on the calcserver where trajectory folders are present

    # select range midday on the latest date to matchstart days earlier
    dt_end = jd2Date(int(jdt_end) + 1, dt_obj=True, tzinfo=datetime.timezone.utc)
    dt_beg = jd2Date(int(jdt_end) + 1 - matchstart, dt_obj=True, tzinfo=datetime.timezone.utc)
    event_time_range = [dt_beg, dt_end]

    dh = RMSDataHandle(basedir, dt_range=event_time_range, db_dir=dbdir, output_dir=basedir,mcmode=1, archivemonths=0)    
    dh.updateTrajectoryDatabase(dt_range=event_time_range)

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
        print('usage: consolidateDistTraj folder_containing_srcdbs targ_dbdir outdir')
        exit(0)
    srcdir = sys.argv[1]
    dbdir = sys.argv[2]
    basedir = os.path.dirname(os.path.normpath(dbdir))
    mergeDatabases(srcdir, dbdir, basedir)
