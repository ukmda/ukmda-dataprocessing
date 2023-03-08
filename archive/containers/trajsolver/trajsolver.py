# Copyright (C) 2018-2023 Mark McIntyre
# trajsolver.py 

import os
import sys
import boto3
import datetime
import tempfile

from wmpl.Trajectory.CorrelateRMS import RMSDataHandle
from wmpl.Utils.Math import generateDatetimeBins
from wmpl.Trajectory.CorrelateEngine import TrajectoryCorrelator, TrajectoryConstraints

# imports are required to load the picklefiles
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON # noqa: F401
from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401


def runCorrelator(dir_path, time_beg, time_end):
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

    # Extract time range
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


# read the source bucket + folder and target buckets + folders from the environment
def getSourceAndTargets():
    srcpth = os.getenv('SRCPATH', default='s3://ukmon-shared/matches/distrib')
    srcpth = srcpth[5:]
    srcbucket = srcpth[:srcpth.find('/')]
    srcpth = srcpth[srcpth.find('/')+1:]

    outpth = os.getenv('OUTPATH', default='s3://ukmon-shared/matches/distrib')
    outpth = outpth[5:]
    outbucket = outpth[:outpth.find('/')]
    outpth = outpth[outpth.find('/')+1:]

    webpth = os.getenv('WEBPATH', default='s3://ukmeteornetworkarchive/dummy')
    webpth = webpth[5:]
    webbucket = webpth[:webpth.find('/')]
    webpth = webpth[webpth.find('/')+1:]

    return srcbucket, srcpth, outbucket, outpth, webbucket, webpth


# extra args for setting the MIME type when uploading to S3. 
# if this isn't set then the files appear as plain text which is no good for images!
def getExtraArgs(fname):
    _, file_ext = os.path.splitext(fname)
    ctyp='text/plain'
    if file_ext=='.jpg': 
        ctyp = 'image/jpeg'
    if file_ext=='.fits': 
        ctyp = 'image/fits'
    elif file_ext=='.png': 
        ctyp = 'image/png'
    elif file_ext=='.bmp': 
        ctyp = 'image/bmp'
    elif file_ext=='.mp4': 
        ctyp = 'video/mp4'
    elif file_ext=='.csv': 
        ctyp = 'text/csv'
    elif file_ext=='.html': 
        ctyp = 'text/html'
    elif file_ext=='.json': 
        ctyp = 'application/json'
    elif file_ext=='.zip': 
        ctyp = 'application/zip'
    extraargs = {'ContentType': ctyp}
    return extraargs


#push solutions to the website, and push the pickle and report to ukmon-shared
def pushToWebsite(s3, localfldr, webbucket, webfldr, outbucket, outpth):
    for root, _, files in os.walk(localfldr):
        for fil in files:
            fullname = os.path.join(localfldr, root, fil)
            fname = os.path.split(fil)[1]
            orbname = os.path.split(root)[1]
            yr = orbname[:4]
            ym = orbname[:6]
            ymd = orbname[:8]
            targkey = f'{webfldr}/{yr}/orbits/{ym}/{ymd}/{orbname}/{fname}'
            print(f'uploading {fname} to s3://{webbucket}/{targkey}')
            s3.meta.client.upload_file(fullname, webbucket, targkey, ExtraArgs = getExtraArgs(fname))
            if 'report' in fname or 'pickle' in fname:
                targkey = f'{outpth}/trajectories/{yr}/{ym}/{ymd}/{orbname}/{fname}'
                print(f'uploading {fname} to s3://{outbucket}/{targkey}')
                s3.meta.client.upload_file(fullname, outbucket, targkey, ExtraArgs = getExtraArgs(fname))
    return


# starting point for the process
def startup(srcfldr, startdt, enddt, isTest=False):
    print(f'processing {srcfldr}')
    print(f"Starting at {datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")

    localfldr = tempfile.mkdtemp()
    canddir = os.path.join(localfldr,'candidates')
    os.makedirs(canddir, exist_ok = True)

    sts_client = boto3.client('sts')

    try: 
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            RoleSessionName="AssumeRoleSession1")

        credentials=assumed_role_object['Credentials']

        s3 = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])    
    except:
        with open('awskeys','r') as inf:
            lis = inf.readlines()
        s3 = boto3.resource('s3',
            aws_access_key_id=lis[0].strip(),
            aws_secret_access_key=lis[1].strip(),
            region_name = 'eu-west-2')

    srcbucket, srcpth, outbucket, outpth, webbucket, webpth = getSourceAndTargets()
    if isTest is True:
        outpth = os.path.join(outpth, 'test')
        
    srckey = f'{srcpth}/{srcfldr}/'

    print(f'fetching data from {srckey}')
    objlist = s3.meta.client.list_objects_v2(Bucket=srcbucket,Prefix=srckey)
    print(objlist)
    if objlist['KeyCount'] > 0:
        keys = objlist['Contents']
        for k in keys:
            fname = k['Key']
            if '.pickle' in fname:
                _, locfname = os.path.split(fname)
                targfile = os.path.join(canddir, locfname)
                print(f'downloading {locfname}')
                s3.meta.client.download_file(srcbucket, fname, targfile)
        runCorrelator(localfldr, startdt, enddt)

        print('uploading data to website')
        trajfldr = os.path.join(localfldr,'trajectories')
        pushToWebsite(s3, trajfldr, webbucket, webpth, outbucket, outpth)

        fname = f'{srcfldr}.json'
        jsonfile = os.path.join(localfldr, 'processed_trajectories.json')
        targkey = f'{srcpth}/{fname}'
        print(f'uploading {jsonfile} to {srcbucket}/{srcpth}')
        s3.meta.client.upload_file(jsonfile, srcbucket, targkey, ExtraArgs = getExtraArgs(fname)) 
    else:
        print('no files found')
    print(f"Finished at {datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    return


if __name__ == '__main__':
    isTest = False
    if len(sys.argv) < 4:
        # default time range
        srcfldr = sys.argv[1]
        rdt = sys.argv[1]
        if 'test' in rdt:
            rdt = rdt[5:]
            isTest = True
        rdt = datetime.datetime.strptime(rdt[:8], '%Y%m%d')
        d1 = (rdt + datetime.timedelta(days = -2)).strftime('%Y%m%d')+'-080000'
        d2 = (rdt + datetime.timedelta(days = 1)).strftime('%Y%m%d')+'-080000'
    else:
        srcfldr = sys.argv[1].strip()
        d1 = sys.argv[2]+'-080000'
        d2 = sys.argv[3]+'-080000'
    print(f'running with {srcfldr}, {d1}, {d2}, {isTest}')
    startup(srcfldr, d1, d2, isTest)
