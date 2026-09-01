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
import shutil
import glob
import sqlite3

import pymysql.cursors

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

    resp = ssmc.get_parameter(Name=f'{env}_calcuser')
    user = resp['Parameter']['Value']
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


def getSqlLoginDetails():
    # retrieve password and host from SSM. This allows me to manage them from Terraform
    ssm = boto3.client('ssm', region_name='eu-west-1')
    res = ssm.get_parameter(Name='prod_dbpw', WithDecryption=True)
    password = res['Parameter']['Value']
    res = ssm.get_parameter(Name='prod_dbhost')
    host = res['Parameter']['Value'] 
    # should really do these too but they won't change often if at all
    user = 'batch'
    db = 'ukmon'
    return host, user, password, db


def removeDeletedTraj(csvfile):
    """
    Remove deleted trajectories from the consolidated match CSV, Parquet, search files and SQL database
    """
    
    csvdata = open(csvfile, 'r').readlines()
    if 'search' in csvfile:
        ts_end = float(csvdata[-1].split(',')[0])
        dt_end = datetime.datetime.fromtimestamp(ts_end, tz=datetime.timezone.utc)
        jdt_end = datetime2JD(dt_end)
    else:
        jdt_end = float(csvdata[-1].split(',')[3]) + 2400000.5
        host, user, passwd, db = getSqlLoginDetails()
        connection = pymysql.connect(host=host, user=user, password=passwd, database=db, cursorclass=pymysql.cursors.DictCursor)  
    jdt_beg = jdt_end - 21

    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    masterdb_path = os.path.join(datadir, 'distrib')
    masterdb = TrajectoryDatabase(db_path=masterdb_path)
    cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
    deltrajs = cur.fetchall()

    i = 0
    j = 0
    # loop over the deleted trajectories, removing the corresponding one from the CSV file and optionally, sql database.
    offs = 4 if 'search' in csvfile else 131
    for traj in deltrajs:
        orbname = traj[0].split('/')[4]
        match = [tr for tr in csvdata if orbname in tr]
        for thismatch in match:
            print(f'removing {orbname} from csv file')
            idx = csvdata.index(thismatch)
            _ = csvdata.pop(idx)
            i += 1
        if 'search' not in csvfile:
            with connection.cursor() as cursor:
                sqlstr = f'update ukmon.matches set status=0 where orbname="{orbname}"'
                cursor.execute(sqlstr)
                result = cursor.fetchall()
                if len(result) > 0:
                    print(f'removing {orbname} from database')
                    j += 1

    masterdb.closeTrajDatabase()
    if 'search' in csvfile:
        print(f'removed {i} trajectories from the search file')
    else:
        connection.commit()
        connection.close()
        print(f'removed {i} trajectories from the text file and {j} from the database')


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


def removeRecalcedTrajCSandS3(calcdir, outpath, webpath, rundate=None):
    """
    Remove trajectories that have been superceded by a rerun that found more data
    NB: this has to be run on the calcserver

    parameters:
    calcdir     path to local trajectories
    outpath     s3 location of trajectories
    webpath     s3 location of web data

    rundate      optional date to perform analysis for. If none, then today's date will be used

    """
    s3 = boto3.resource('s3')
    if not rundate:
        rundate = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y%m%d')

    dbhandle = sqlite3.connect(os.path.join(calcdir, 'dbs', 'trajectories.db'))

    logs = glob.glob(os.path.join(calcdir, 'logs', f'correlate_rms_{rundate}*.log'))
    if len(logs) == 0:
        print(f'no logfile for {rundate}')
        return 

    localdel = 0

    for logf in logs:
        loglines = open(logf).readlines()
        removed = [x[x.find('trajectories'):].replace('...','').strip() for x in loglines if 'Removing the previous' in x]
        saved = [x[x.find('trajectories'):].strip() for x in loglines if 'saved' in x and 'to ./trajectories' in x]

        # skip any rows where the new and old names are the same
        for sav in saved:
            if sav in removed:
                removed.pop(removed.index(sav))

        # now run through any remaining removed orbits and make sure they're removed from everywhere
        for orbfldr in removed:
            # local files first
            localpath = os.path.join(calcdir, orbfldr)
            if os.path.isdir(localpath):
                shutil.rmtree(localpath)
                localdel += 1
                print(f'removed {orbfldr}')

            # make sure orb is marked deleted in sqlite
            sqlstr = f'update trajectories set status=0 where traj_file_path like "{orbfldr}%"'
            dbhandle.execute(sqlstr)

            # now remove the folder from shared S3
            sharedkey = f'{outpath}/{orbfldr}'
            bucket = sharedkey[5:].split('/')[0]
            prefix = sharedkey[len(bucket)+6:]
            bucket = s3.Bucket(bucket)
            bucket.objects.filter(Prefix=prefix).delete()

            # lastly web S3
            spls = orbfldr.split('/')
            sharedkey = f'{webpath}/{spls[1]}/orbits/{spls[2]}/{spls[3]}/{spls[4]}'
            bucket = sharedkey[5:].split('/')[0]
            prefix = sharedkey[len(bucket)+6:]
            bucket = s3.Bucket(bucket)
            bucket.objects.filter(Prefix=prefix).delete()

    print(f'removed {localdel} folders from calcserver')
    dbhandle.commit()
    dbhandle.close()

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
