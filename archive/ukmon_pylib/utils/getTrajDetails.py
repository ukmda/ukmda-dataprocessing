import os
import sys
import datetime
import argparse

from wmpl.Utils.TrajConversions import jd2Date
from wmpl.Utils.Pickling import loadPickle


def getStnsAndDate(traj):
    if not os.path.isfile(traj):
        return [None]*7
    picklepath, picklefile = os.path.split(traj)
    traj = loadPickle(picklepath, picklefile)

    fmtime = os.path.getmtime(os.path.join(os.path.expanduser(picklepath), picklefile))
    fmtime = datetime.datetime.fromtimestamp(fmtime).replace(tzinfo=datetime.timezone.utc)
    stns = [obs.station_id for obs in traj.observations if obs.ignore_station is False]
    obsids = [obs.obs_id for obs in traj.observations if obs.ignore_station is False]
    refdt = jd2Date(traj.jdt_ref, dt_obj=True)

    longname = ''
    if hasattr(traj, 'longname'):
        longname = traj.longname
    pre_mc_longname = ''
    if hasattr(traj, 'pre_mc_longname'):
        pre_mc_longname = traj.pre_mc_longname

    traj_id = ''
    if hasattr(traj, 'traj_id'):
        traj_id = traj.traj_id
    cand_id = ''
    if hasattr(traj, 'cand_id'):
        cand_id = traj.cand_id

    return traj_id, cand_id, str(refdt), obsids, longname, pre_mc_longname, str(fmtime)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Examine a trajectory pickle file')
    arg_parser.add_argument('traj_path', metavar='TRAJ_PATH', type=str, help='Full path to the trajectory pickle')
    cml_args = arg_parser.parse_args()

    retvals = getStnsAndDate(cml_args.traj_path)
    print(f'traj_id :    {retvals[0]}')
    print(f'cand_id :    {retvals[1]}')
    print(f'obs_ids :    {retvals[3]}')
    print(f'ref_dt  :    {retvals[2]}')
    print(f'longname:    {retvals[4]}')
    print(f'pre-long:    {retvals[5]}')
    print(f'savetime:    {retvals[6]}')
