"""
copyright Mark McIntyre, 2026-

Extract some key details from a trajectory pickle file

- jdt_ref 
- station IDs
- longname
- pre-mc longname
- file creation time
- observation IDs

"""
import os
import sys
import datetime
import argparse

from wmpl.Utils.TrajConversions import jd2Date
from wmpl.Utils.Pickling import loadPickle


def getStnsAndDate(traj, trajdir=None):
    longname = ''
    pre_mc_longname = ''
    if not os.path.isfile(traj):
        traj = os.path.join(trajdir, traj)
    picklepath, picklefile = os.path.split(traj)
    if not os.path.isfile(traj):
        print(f'unable to find {traj}')
        return None, None, None, None, None, None
    
    traj = loadPickle(picklepath, picklefile)

    fmtime = os.path.getmtime(os.path.join(os.path.expanduser(picklepath), picklefile))
    fmtime = datetime.datetime.fromtimestamp(fmtime).replace(tzinfo=datetime.timezone.utc)
    stns = [obs.station_id for obs in traj.observations if obs.ignore_station is False]
    obsdts = [obs.jdt_ref for obs in traj.observations if obs.ignore_station is False]
    idlist = [obs.obs_id for obs in traj.observations if obs.ignore_station is False]
    refdt = jd2Date(traj.jdt_ref, dt_obj=True)
    if hasattr(traj, 'longname'):
        longname = traj.longname
    if hasattr(traj, 'pre_mc_longname'):
        pre_mc_longname = traj.pre_mc_longname
    print(refdt, stns, longname, pre_mc_longname, fmtime, idlist)
    return str(refdt), stns, longname, pre_mc_longname, str(fmtime), idlist


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Get basic details of a trajectory pickle')
    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, 
        help='Trajectory pickle to analyse')
    cml_args = arg_parser.parse_args()

    try:
        getStnsAndDate(cml_args.dir_path)
    except Exception:
        print('unable to get details, probably not trajectory pickle')
