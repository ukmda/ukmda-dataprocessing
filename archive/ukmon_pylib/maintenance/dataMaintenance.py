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
    hname = os.getenv('HOSTNAME', default='none')
    env = os.getenv('RUNTIME_ENV', default='DEV').lower()

    if hname != 'ukmonhelper2':
        sess = boto3.Session(profile_name='default')
        ssmc = sess.client('ssm', region_name='eu-west-2')
        ec2 = boto3.client('ec2', region_name='eu-west-2')
    else:
        ssmc = boto3.client('ssm', region_name='eu-west-2')
        prof = os.getenv('UKMPROFILE',default='ukmonshared')
        sess = boto3.Session(profile_name=prof)
        ec2 = sess.client('ec2', region_name='eu-west-2')
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
    Remove deleted trajectories from the consolidated match CSV and Parquet files
    and from the search index. 
    """

    csvdata = open(csvfile, 'r').readlines()
    if 'search' in csvfile:
        ts_end = float(csvdata[-1].split(',')[0])
        dt_end = datetime.datetime.fromtimestamp(ts_end, tz=datetime.timezone.utc)
        jdt_end = datetime2JD(dt_end)
    else:
        jdt_end = float(csvdata[-1].split(',')[3]) + 2400000.5

    jdt_beg =jdt_end - 21

    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    masterdb_path = os.path.join(datadir, 'distrib')
    masterdb = TrajectoryDatabase(db_path=masterdb_path)
    cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
    deltrajs = cur.fetchall()
    masterdb.closeTrajDatabase()

    i=0
    for traj in deltrajs:
        fldr = os.path.basename(os.path.dirname(traj[0]))
        match = [tr for tr in csvdata if fldr in tr]
        if len(match) > 0:
            for thismtch in match:
                print(f'removing {fldr}')
                idx = csvdata.index(thismtch)
                _ = csvdata.pop(idx)
                i += 1
    print(f'removed {i} trajectories')

    open(csvfile, 'w').writelines(csvdata)

    if 'search' not in csvfile:
        df = pd.read_csv(csvfile, skipinitialspace=True)
        df = df.drop_duplicates(subset=['_mjd','_sol','_ID1','_ra_o','_dc_o','_amag','_ra_t','_dc_t'])
        df.to_csv(csvfile, index=False)

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


def removeDelTrajFromDb():
    dt_end = datetime.datetime.now(tz=datetime.timezone.utc)
    jdt_end = datetime2JD(dt_end)
    jdt_beg =jdt_end - 7

    # get list of deleted trajectories
    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    masterdb_path = os.path.join(datadir, 'distrib')
    masterdb = TrajectoryDatabase(db_path=masterdb_path)
    cur = masterdb.dbhandle.execute(f'select traj_file_path from trajectories where status=0 and jdt_ref >= {jdt_beg} and jdt_ref <={jdt_end}')
    deltrajs = cur.fetchall()
    masterdb.closeTrajDatabase()

    # get connection to the SQL database
    host, user, passwd, db = getSqlLoginDetails()
    connection = pymysql.connect(host=host, user=user, password=passwd, database=db, cursorclass=pymysql.cursors.DictCursor)  

    count = 0
    for traj in deltrajs:
        fldr = os.path.basename(os.path.dirname(traj[0]))
        sqlstr = f"delete from matches where orbname like '{fldr}%'"
        with connection.cursor() as cursor:
            cursor.execute(sqlstr)
            result = cursor.fetchall()
            count += len(result)
    connection.commit()
    connection.close()
    print(f'cleaned up {count} trajectories')
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
