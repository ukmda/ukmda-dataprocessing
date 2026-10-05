"""
copyright Mark McIntyre, 2026-

Extract some key details from a candidate pickle file
For each observation:
- station ids
- jdt_ref 
- obs time data
- obs ref date
- obs time offsets

"""
import os
import sys
import argparse
from wmpl.Trajectory.CorrelateRMS import MeteorPointRMS, MeteorObsRMS, PlateparDummy # noqa: F401
from wmpl.Utils.Pickling import loadPickle
from wmpl.Utils.TrajConversions import jd2Date


def analysePickle(pickname):
    cand = loadPickle(*os.path.split(pickname))
    for obs, met_obs, _ in cand:
        print(f'{obs.station_id} {jd2Date(obs.jdt_ref, dt_obj=True)} {obs.time_data} {met_obs.reference_dt}, {[d.time_rel for d in met_obs.data]}')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Get basic details of a candidate pickle - list of observations and other data')
    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, 
        help='Candidate pickle to analyse')
    cml_args = arg_parser.parse_args()

    try:
        analysePickle(cml_args.dir_path)
    except:
        print('unable to extract details, probably not a candidate pickle')
