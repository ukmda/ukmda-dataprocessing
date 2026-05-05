#
# python script to help clear out archive data
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import boto3
import argparse
import paramiko
from scp import SCPClient
from time import sleep
import pandas as pd
import datetime
import json
import operator

from wmpl.Utils.TrajConversions import datetime2JD
from wmpl.Trajectory.CorrelateDB import TrajectoryDatabase


def findInputDataByMonth(yyyymm, archbucket, outdir):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)

    # get list of files to be removed from S3
    files = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/UK')]
    befiles = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/BE')]
    iefiles = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/IE')]
    files = files + befiles + iefiles

    mthfiles = [file for file in files if f'_{yyyymm}' in file and f'_{yyyymm}_' not in file]

    # get list of directories to be removed from calcserver
    dirs = [os.path.split(d)[0] for d in mthfiles]
    dirs = list(set(dirs))
    dirs.sort()
    outfname = os.path.join(outdir, f'todelete-{yyyymm}.txt')
    with open(outfname, 'w') as outf:
        for dir in dirs:
            outf.write(f'{dir}\n')
    return mthfiles, outfname


def deleteS3FilesByMonth(flist, archbucket):
    print('clearing down S3')
    s3 = boto3.client('s3')
    chunk_size = 900
    chunked_list = [flist[i:i + chunk_size] for i in range(0, len(flist), chunk_size)]
    for ch in chunked_list:
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': k} for k in ch]
        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
    print('S3 done')
    return 


def deleteFromCalcServerByMonth(outfname):
    env = os.getenv('RUNTIME_ENV', default='DEV').lower()

    ssmc = boto3.client('ssm', region_name='eu-west-2')
    ec2 = boto3.client('ec2', region_name='eu-west-2')

    resp = ssmc.get_parameter(Name=f'{env}_calcinstance')
    instId = resp['Parameter']['Value']
    print('clearing down calcserver')    
    needstart = False
    sts = ec2.describe_instances(InstanceIds=[instId])
    currstate = sts['Reservations'][0]['Instances'][0]['State']['Name']
    if currstate != 'running':
        print('starting server')
        needstart = True
        sts = ec2.start_instances(InstanceIds=[instId])
        currstate = sts['StartingInstances'][0]['CurrentState']
        while currstate != 'running':
            sleep(5)
            sts = ec2.describe_instances(InstanceIds=[instId])
            currstate = sts['Reservations'][0]['Instances'][0]['State']['Name']
            server = sts['Reservations'][0]['Instances'][0]['PrivateIpAddress']

    # server='172.32.16.136'
    user='ec2-user'
    serverkey = os.getenv('SERVERSSHKEY')
    k = paramiko.RSAKey.from_private_key_file(serverkey)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = server, username = user, pkey = k)
    scpcli = SCPClient(c.get_transport())
    scpcli.put(outfname, outfname)
    command = f'cat {outfname} | while read i ; do rm -Rf ~/ukmon-shared/$i ; done > /tmp/{outfname}.log 2>&1'
    stdin, stdout, stderr = c.exec_command(command)

    # only stop if it wasn't already running - to avoid damaging data runs
    if needstart is True:
        print('stoppping server again')
        sts = ec2.stop_instances(InstanceIds=[instId])
    print('calcserver done')    
    return 


def removeDeletedTraj(csvfile):
    """
    Remove deleted trajectories from the consolidated match CSV, Parquet and search files
    """

    csvdata = open(csvfile, 'r').readlines()
    if 'search' in csvfile:
        ts_end = float(csvdata[-1].split(',')[0])
        dt_end = datetime.datetime.fromtimestamp(ts_end, tz=datetime.timezone.utc)
        jdt_end = datetime2JD(dt_end)
    else:
        jdt_end = float(csvdata[-1].split(',')[3]) + 2400000.5
    jdt_beg = jdt_end - 21

    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    masterdb_path = os.path.join(datadir, 'distrib')
    masterdb = TrajectoryDatabase(db_path=masterdb_path)
    cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
    deltrajs = cur.fetchall()

    i=0
    # loop over the deleted trajectories, removing the corresponding one from the CSV file.
    # Note that there's no need to update the MariaDB database, as it is populated
    # from the CSV file *after* it has been purged
    offs = 4 if 'search' in csvfile else 131
    for traj in deltrajs:
        cur = masterdb.dbhandle.execute(f'select jdt_ref, participating_stations from trajectories where traj_file_path="{traj[0]}" and status=0')
        thistraj = cur.fetchall()
        if len(thistraj) == 1: 
            fldr = os.path.basename(os.path.dirname(traj[0]))

            # find the rows in the CSV file that correspond to the deleted trajectory
            # then go through them and compare obs_ids. The one with the same obs_ids 
            # is the one we want to remove
            match = [tr for tr in csvdata if fldr in tr]
            obs_ids = thistraj[0][1]
            obs_ids_str = ';'.join(json.loads(obs_ids)) + ';'
            for thismtch in match:
                if thismtch.split(',')[offs] == obs_ids_str:
                    print(f'removing {fldr}')
                    idx = csvdata.index(thismtch)
                    _ = csvdata.pop(idx)
                    i += 1
                    break
        else:
            print(f'skipping {traj[0]} as there are {len(thistraj)} active trajs with the same path')
    masterdb.closeTrajDatabase()
    print(f'removed {i} trajectories from the text file')

    # save the CSV file again
    open(csvfile, 'w').writelines(csvdata)

    if 'search' not in csvfile:
        df = pd.read_csv(csvfile, skipinitialspace=True)
        df = df.drop_duplicates(subset=['_mjd','_sol','_ID1','_ra_o','_dc_o','_amag','_ra_t','_dc_t'])
        df.to_csv(csvfile, index=False)

    return 


def removeDeletedTrajCsv(csvloc, targloc):
    """
    Remove csv files corresponding to deleted trajectories before they are 
    consolidated into the annual CSV and Parquet files
    """
    srcbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]

    csvfiles = []
    s3 = boto3.client('s3')
    print('checking in ', csvloc, 'sending to ', targloc)
    res = s3.list_objects(Bucket=srcbucket, Prefix=csvloc)
    if 'Contents' in res:
        for k in res['Contents']:
            csvname = k["Key"]
            csv_dt = datetime.datetime.strptime(os.path.basename(k["Key"])[:22], "%Y%m%d-%H%M%S.%f")
            csvfiles.append({"name":csvname, "dt":csv_dt})
        csvfiles.sort(key=operator.itemgetter('name'))
        jdt_beg = datetime2JD(csvfiles[0]['dt'])
        jdt_end = datetime2JD(csvfiles[-1]['dt'])

        datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
        masterdb_path = os.path.join(datadir, 'distrib')
        masterdb = TrajectoryDatabase(db_path=masterdb_path)
        cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
        deltrajs = cur.fetchall()

        i=0
        # loop over the deleted trajectories, removing the corresponding CSV file.
        for del_traj in deltrajs:
            cur = masterdb.dbhandle.execute(f'select jdt_ref, participating_stations from trajectories where traj_file_path="{del_traj[0]}" and status=0')
            thistraj = cur.fetchall()
            if len(thistraj) == 1: 
                obs_ids = thistraj[0][1]
                obs_ids_str = ';'.join(json.loads(obs_ids)) + ';'
                fldr = os.path.basename(os.path.dirname(del_traj[0]))[:19].replace('_', '-')

                matched_csvs = [x for x in csvfiles if fldr in x['name']]
                for csv in matched_csvs:
                    csvdata = s3.get_object(Bucket=srcbucket, Key=csv['name'])['Body'].read()
                    csv_obs_ids = csvdata.decode('utf-8').split(',')[131].strip()
                    if csv_obs_ids == obs_ids_str:
                        # we have a match to within 0.001s and with the same observations
                        print(f'removing {fldr}')
                        bare_csv_name = os.path.basename(matched_csvs[0]['name'])
                        yr = bare_csv_name[:4]
                        destkey = f"{targloc}/{yr}/{bare_csv_name}"
                        s3.copy({"Bucket":srcbucket,"Key":csv['name']}, srcbucket, destkey)       
                        s3.delete_object(Bucket=srcbucket, Key=matched_csvs[0]['name'])
                        i += 1
                        break
            else:
                print(f'skipping {del_traj[0]} as there are {len(thistraj)} inactive trajs with the same path')
        masterdb.closeTrajDatabase()
        print(f'removed {i} trajectories from the text file')
    else:
        print('no fullcsv files to process')

    return 


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Find and clear down historical raw data.")

    arg_parser.add_argument('periods', metavar='PERIODS', nargs='+', type=str,
        help='Period to clear down in yyyymm format.')

    cml_args = arg_parser.parse_args()
    dtstr = cml_args.periods[0]
    print(f'Clearing data for {dtstr}')

    archbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    outdir = os.getenv('TMP', default='/tmp')

    mthfiles, outfname = findInputDataByMonth(dtstr, archbucket, outdir)
    deleteS3FilesByMonth(mthfiles, archbucket)
    deleteFromCalcServerByMonth(outfname)
