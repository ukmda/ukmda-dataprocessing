# load a Trajectory sqlite database and look for duplicates

import pandas as pd
import os
import sys
import datetime
import argparse

from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase
from wmpl.Utils.TrajConversions import datetime2JD


def atleastOneObs(obs_ids,next_obs_ids):
    if obs_ids is None or next_obs_ids is None:
        return False
    return any(i in next_obs_ids for i in obs_ids)


def findDuplicatesByObsId(df):
    df['obs_ids_next'] = df.obs_ids.shift(-1)
    same_obs = df.query('obs_ids == obs_ids_next')
    df['overlapstats'] = df.apply(lambda row: atleastOneObs(row.obs_ids, row.obs_ids_next), axis=1)
    common_obs = df[df.overlapstats]
    print(f'there are {len(df)} trajectories in the period')
    print(f'there are {len(common_obs)} ({round(100*len(common_obs)/len(df),2)}%) with at least one common station')
    print(f'there are {len(same_obs)} ({round(100*len(same_obs)/len(df),2)}%) with the same stations')
    return common_obs, same_obs


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Analyse a trajectory database')
    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, help='Path to database')
    arg_parser.add_argument('db_name', metavar='DB_NAME', type=str, help='database name')
    cml_args = arg_parser.parse_args()

    if not os.path.isfile(os.path.join(cml_args.dir_path, cml_args.db_name)):
        print('unable to open database')
        exit(0)


    tdb = TrajectoryDatabase(cml_args.dir_path, db_name=cml_args.db_name)
    jdt_range = [datetime2JD(datetime.datetime(2025,1,1)), datetime2JD(datetime.datetime.now())]
    trajs = tdb.getTrajBasics('.', jdt_range)
    df = pd.DataFrame(trajs)
    df.sort_values(by='jdt_ref', inplace=True)

    common_obs, same_obs = findDuplicatesByObsId(df)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print(common_obs.traj_file_path)
    print(same_obs.traj_file_path)
