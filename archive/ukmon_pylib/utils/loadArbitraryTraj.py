"""
copyright Mark McIntyre, 2026-

A script to load an arbitrary set of trajectories in .pickle form into the Trajectory SQLite database

"""
from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced

import os
import sys
import logging
import argparse

log = logging.getLogger("traj_correlator")


def loadDb(trajpath, dbpath, dbname, purge_records=True):
    trajdb = TrajectoryDatabase(dbpath, db_name=dbname, verbose=True, purge_records=purge_records)
    for pth, dirs, files in os.walk(trajpath):
        for fil in files:
            if '.pickle' in fil:
                res = trajdb.addTrajectory(TrajectoryReduced(os.path.join(pth, fil)),verbose=True)
                if not res:
                    log.warning(f'failed to add {fil}')

    res = trajdb.dbhandle.execute('select count(*) from trajectories').fetchall()
    print(f'added {res} ')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='load a set of trajectory pickles into the sqlite trajectory database')

    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, 
        help='Path to folder tree with trajectory pickle files')

    arg_parser.add_argument('db_path', metavar='DB_PATH', type=str, 
        help='Path to trajectory database')

    arg_parser.add_argument('db_name', metavar='DB_NAME', type=str, default='trajectories.db',
        help='Datbase name - default trajectories.db')

    cml_args = arg_parser.parse_args()

    log.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(
        fmt='%(asctime)s-%(levelname)-5s-%(module)-15s:%(lineno)-5d- %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    log.addHandler(console_handler)

    loadDb(cml_args.dir_path, cml_args.db_path, cml_args.db_name)