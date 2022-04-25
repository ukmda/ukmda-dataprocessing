# trajsolver.py 

import os
import sys
import boto3
import datetime
import tempfile
import tarfile

from wmpl.Trajectory.CorrelateRMS import RMSDataHandle
from wmpl.Utils.Math import generateDatetimeBins
from wmpl.Trajectory.CorrelateEngine import TrajectoryCorrelator, TrajectoryConstraints
# imports are NOT unused, they're required to load the picklefiles
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON, \
    MeteorObsRMS, PlateparDummy, MeteorPointRMS


def prepareCorrelator(dir_path, timerange):
    # Init trajectory constraints
    maxtoffset = 10.0
    maxstationdist = 600.0
    maxveldiff = 25.0
    disablemc = False
    saveplots = True
    velpart = 0.40
    uncerttime = False
    distribute = 2

    trajectory_constraints = TrajectoryConstraints()
    trajectory_constraints.max_toffset = maxtoffset
    trajectory_constraints.max_station_dist = maxstationdist
    trajectory_constraints.max_vel_percent_diff = maxveldiff
    trajectory_constraints.run_mc = not disablemc
    trajectory_constraints.save_plots = saveplots
    trajectory_constraints.geometric_uncert = not uncerttime

    # Clock for measuring script time
    t1 = datetime.datetime.utcnow()

    # If auto run is enabled, compute the time range to use
    event_time_range = None

    # If the time range to use is given, use it
    if timerange is not None:

        # Extract time range
        time_beg, time_end = timerange.strip("(").strip(")").split(",")
        dt_beg = datetime.datetime.strptime(time_beg, "%Y%m%d-%H%M%S")
        dt_end = datetime.datetime.strptime(time_end, "%Y%m%d-%H%M%S")

        print("Custom time range:")
        print("    BEG: {:s}".format(str(dt_beg)))
        print("    END: {:s}".format(str(dt_end)))

        event_time_range = [dt_beg, dt_end]

    # Init the data handle
    dh = RMSDataHandle(dir_path, event_time_range)

    # If there is nothing to process, stop, unless we're in distributed 
    # processing mode 2 
    if not dh.processing_list and distribute !=2:
        print()
        print("Nothing to process!")
        print("Probably everything is already processed.")
        print("Exiting...")
        sys.exit()


    ### GENERATE MONTHLY TIME BINS ###
    
    # Find the range of datetimes of all folders (take only those after the year 2000)
    proc_dir_dts = [entry[3] for entry in dh.processing_list if entry[3] is not None]
    proc_dir_dts = [dt for dt in proc_dir_dts if dt > datetime.datetime(2000, 1, 1, 0, 0, 0)]

    # Reject all folders not within the time range of interest +/- 1 day
    if event_time_range is not None:

        dt_beg, dt_end = event_time_range

        proc_dir_dts = [dt for dt in proc_dir_dts
            if (dt >= dt_beg - datetime.timedelta(days=1)) and (dt <= dt_end + datetime.timedelta(days=1))]
        # to avoid excluding all possible dates
        if proc_dir_dts == []: 
            proc_dir_dts=[dt_beg - datetime.timedelta(days=1), dt_end + datetime.timedelta(days=1)]

    # Determine the limits of data
    proc_dir_dt_beg = min(proc_dir_dts)
    proc_dir_dt_end = max(proc_dir_dts)

    # Split the processing into monthly chunks
    dt_bins = generateDatetimeBins(proc_dir_dt_beg, proc_dir_dt_end, bin_days=30)

    print()
    print("ALL TIME BINS:")
    print("----------")
    for bin_beg, bin_end in dt_bins:
        print("{:s}, {:s}".format(str(bin_beg), str(bin_end)))


    ### ###


    # Go through all chunks in time
    for bin_beg, bin_end in dt_bins:

        print()
        print("{}".format(datetime.datetime.now().strftime('%Y-%m-%dZ%H:%M:%S')))
        print("PROCESSING TIME BIN:")
        print(bin_beg, bin_end)
        print("-----------------------------")
        print()

        # Load data of unprocessed observations
        dh.unpaired_observations = dh.loadUnpairedObservations(dh.processing_list, dt_range=(bin_beg, bin_end))

        # Run the trajectory correlator
        tc = TrajectoryCorrelator(dh, trajectory_constraints, velpart, data_in_j2000=True, distribute=distribute)
        tc.run(event_time_range=event_time_range)
    
    print("Total run time: {:s}".format(str(datetime.datetime.utcnow() - t1)))
    return 


def startup(srcfldr, timerange):
    print(f'processing {srcfldr}')
    print(f"Starting at {datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")

    localfldr = tempfile.mkdtemp()
    canddir = os.path.join(localfldr,'candidates')
    os.makedirs(canddir, exist_ok = True)

    if os.path.isfile('awskeys'):
        with open('awskeys') as inf:
            keys = inf.readlines()
        spls = keys[1].split(',')
        acckey = spls[2]
        secret = spls[3]
    else:
        print('key file missing, unable to continue')
        return 
    s3 = boto3.resource('s3', aws_access_key_id=acckey, aws_secret_access_key = secret)

    srcbucket = 'ukmon-shared'
    srckey = f'matches/disttest/{srcfldr}/candidates/'

    objlist = s3.meta.client.list_objects_v2(Bucket=srcbucket,Prefix=srckey)
    if objlist['KeyCount'] > 0:
        keys = objlist['Contents']
        for k in keys:
            fname = k['Key']
            if '.pickle' in fname:
                _, locfname = os.path.split(fname)
                targfile = os.path.join(canddir, locfname)
                print(f'downloading {locfname}')
                s3.meta.client.download_file(srcbucket, fname, targfile)

    prepareCorrelator(localfldr, timerange)

    print('creating tarfile')
    trajfldr = os.path.join(localfldr,'trajectories')
    outputname = os.path.join(localfldr, srcfldr + '.tgz')
    with tarfile.open(outputname, 'w:gz') as tar:
        tar.add(trajfldr, arcname=os.path.basename(trajfldr))
        tar.add(os.path.join(localfldr, 'processed_trajectories.json'))
    
    targkey = f'matches/disttest/{srcfldr}.tgz'
    print(f'uploading {outputname} to {targkey}')
    s3.meta.client.upload_file(outputname, srcbucket, targkey, ExtraArgs = {'ContentType': 'application/gzip'})

    print(f"Finished at {datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    return


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('not enough arguments - must pass source folder and daterange')
    else:
        startup(sys.argv[1], sys.argv[2])
