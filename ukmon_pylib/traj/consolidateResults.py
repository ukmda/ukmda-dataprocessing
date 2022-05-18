import os

# imports are required to load the picklefiles
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON 
#from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401


class dummyMeteorObsRMS(object):
    def __init__(self, station_code, id):
        self.station_code = station_code
        self.id = id


def mergeDatabases(targdir, fldrname, masterfile):
    newdb = os.path.join(targdir, fldrname + '.json')
    mergedb = DatabaseJSON(newdb)
    mastdb = DatabaseJSON(masterfile)
    mastdb.db_file_path = masterfile
    # merge successful trajectories
    for traj in mergedb.trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = '/home/ec2-user/data/RMSCorrelate/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj)
    # merge failed trajectories 
    for traj in mergedb.failed_trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.failed_trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = '/home/ec2-user/data/RMSCorrelate/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj, failed=True)
    # merge paired obs data
    for p in mergedb.paired_obs:
        ids = mergedb.paired_obs[p]
        for id in ids:
            met_obs = dummyMeteorObsRMS(p, id)
            mastdb.addPairedObservation(met_obs)
    # save the master DB again
    mastdb.save()
    return
