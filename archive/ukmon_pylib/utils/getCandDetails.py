# python script to analyse candidates

import os
import sys
import datetime
from wmpl.Trajectory.CorrelateRMS import MeteorPointRMS, MeteorObsRMS, PlateparDummy # noqa: F401
from wmpl.Utils.Pickling import loadPickle
from wmpl.Utils.TrajConversions import jd2Date
import argparse


def analyseCandidate(pickname):
    cand = loadPickle(*os.path.split(pickname))
    cand_id = os.path.splitext(os.path.split(pickname)[-1])[0]
    obs_ids = [obs.obs_id for _, obs, _ in cand] 
    fmtime = os.path.getmtime(pickname)
    fmtime = datetime.datetime.fromtimestamp(fmtime).replace(tzinfo=datetime.timezone.utc)

#    for obs, met_obs, _ in cand:
#        print(f'{obs.station_id} {jd2Date(obs.jdt_ref, dt_obj=True)} {obs.time_data} {met_obs.reference_dt}, {[d.time_rel for d in met_obs.data]}')
    return cand_id, obs_ids, fmtime


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Examine a candidate pickle file')
    arg_parser.add_argument('candname', metavar='CANDNAME', type=str, help='Full path to the candidate pickle')
    cml_args = arg_parser.parse_args()

    retvals = analyseCandidate(cml_args.candname)
    print(f'cand_id :    {retvals[0]}')
    print(f'obs_ids :    {retvals[1]}')
    print(f'savetime:    {retvals[2]}')
