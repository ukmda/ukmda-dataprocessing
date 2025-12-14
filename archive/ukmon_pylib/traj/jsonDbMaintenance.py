# small script to archive off old data from the JSON database
import datetime
import os 
import sys
from dateutil.relativedelta import relativedelta

from wmpl.Utils.TrajConversions import datetime2JD, jd2Date
from wmpl.Trajectory.CorrelateRMS import DatabaseJSON

# Name of json file with the list of processed directories
JSON_DB_NAME = "processed_trajectories.json"


def archiveOldRecords(db, db_dir, older_than=3):
    """
    Archive off old records to keep the database size down

    Keyword Arguments:
        older_than: [int] number of months to keep, default 3
    """
    class DummyMetObs():
        def __init__(self, station, obs_id):
            self.station_code = station
            self.id = obs_id

    archdate = datetime.datetime.now(datetime.timezone.utc) - relativedelta(months=older_than)
    archdate_jd = datetime2JD(archdate)

    arch_db_path = os.path.join(db_dir, 'archive', f'{archdate.strftime("%Y%m")}_{JSON_DB_NAME}')
    os.makedirs(os.path.join(db_dir, 'archive'), exist_ok=True)
    archdb = DatabaseJSON(arch_db_path)

    for traj in [t for t in db.trajectories if t < archdate_jd]:
        if traj < archdate_jd:
            archdb.addTrajectory(None, db.trajectories[traj], False)
            del db.trajectories[traj]

    for traj in [t for t in db.failed_trajectories if t < archdate_jd]:
        if traj < archdate_jd:
            archdb.addTrajectory(None, db.failed_trajectories[traj], True)
            del db.failed_trajectories[traj]

    for station in db.processed_dirs:
        arch_processed = [dirname for dirname in db.processed_dirs[station] if 
                            datetime.datetime.strptime(dirname[14:22], '%Y%m%d').replace(tzinfo=datetime.timezone.utc) < archdate]
        for dirname in arch_processed:
            archdb.addProcessedDir(station, dirname)
            db.processed_dirs[station].remove(dirname)

    for station in db.paired_obs:
        arch_processed = [obs_id for obs_id in db.paired_obs[station] if 
                            datetime.datetime.strptime(obs_id[7:15], '%Y%m%d').replace(tzinfo=datetime.timezone.utc) < archdate]
        for obs_id in arch_processed:
            archdb.addPairedObservation(DummyMetObs(station, obs_id))
            db.paired_obs[station].remove(obs_id)

    archdb.save()
    db.save()
    return db


def clearDownHistoricArchive(database_path, mthsback=1):
    db = DatabaseJSON(database_path)

    if len(list(db.failed_trajectories.keys()))==0 and len(list(db.trajectories.keys()))==0:
        print('nothing to do')
        return
    elif len(list(db.failed_trajectories.keys()))==0:
        latest = jd2Date(max(list(db.trajectories.keys())), dt_obj=True)
    elif len(list(db.trajectories.keys()))==0:
        latest = jd2Date(max(list(db.failed_trajectories.keys())), dt_obj=True)
    else:
        latest = jd2Date(max(max(list(db.trajectories.keys())), max(list(db.failed_trajectories.keys()))), dt_obj=True)
    print('processing', database_path)
    archdate = latest - relativedelta(months=mthsback)
    archdate = archdate.replace(day=1, hour=12, minute=0, second=0).replace(tzinfo=datetime.timezone.utc)
    archdate_jd = datetime2JD(archdate)

    for traj in [t for t in db.trajectories if t < archdate_jd]:
        if traj < archdate_jd:
            del db.trajectories[traj]

    for traj in [t for t in db.failed_trajectories if t < archdate_jd]:
        if traj < archdate_jd:
            del db.failed_trajectories[traj]

    for station in db.processed_dirs:
        arch_processed = [dirname for dirname in db.processed_dirs[station] if 
                            datetime.datetime.strptime(dirname[14:22], '%Y%m%d').replace(tzinfo=datetime.timezone.utc) < archdate]
        for dirname in arch_processed:
            db.processed_dirs[station].remove(dirname)

    for station in db.paired_obs:
        arch_processed = [obs_id for obs_id in db.paired_obs[station] if 
                            datetime.datetime.strptime(obs_id[7:15], '%Y%m%d').replace(tzinfo=datetime.timezone.utc) < archdate]
        for obs_id in arch_processed:
            db.paired_obs[station].remove(obs_id)

    db.save()
    return 


if __name__ == '__main__':
    db_dir = sys.argv[1]
    database_path = os.path.join(db_dir, JSON_DB_NAME)
    db = DatabaseJSON(database_path)
    soonest = jd2Date(min(min(list(db.trajectories.keys())), min(list(db.failed_trajectories.keys()))), dt_obj=True)
    nowdt = datetime.datetime.now()
    mthsback = int((nowdt - soonest).days/30)
    for i in range(mthsback, 2, -1):
        print(f'archiving {i} months back')
        db = archiveOldRecords(db, db_dir, i)
