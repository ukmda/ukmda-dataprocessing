#
# python script to help clear out archive data
#

import os
import sys
import boto3
import argparse
import paramiko
from scp import SCPClient


def findInputDataByMonth(yyyymm, archbucket, outdir):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)

    # get list of files to be removed from S3
    files = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/UK')]
    befiles = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/BE')]
    iefiles = [os.key for os in bucket.objects.filter(Prefix='matches/RMSCorrelate/IE')]
    files = files + befiles + iefiles

    mthfiles = [file for file in files if f'_{yyyymm}' in file  and f'_{yyyymm}_' not in file]

    # get list of directories to be removed from calcserver
    dirs = [ os.path.split(d)[0] for d in mthfiles]
    dirs = list(set(dirs))
    dirs.sort()
    outfname = os.path.join(outdir, f'todelete-{yyyymm}.txt')
    with open(outfname, 'w') as outf:
        for dir in dirs:
            outf.write(f'{dir}\n')
    return mthfiles, outfname


def deleteS3FilesByMonth(flist, archbucket):
    s3 = boto3.client('s3')
    chunk_size = 900
    chunked_list = [flist[i:i + chunk_size] for i in range(0, len(flist), chunk_size)]
    for ch in chunked_list:
        delete_keys = {'Objects' : []}
        delete_keys['Objects'] = [{'Key' : k} for k in ch]
        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
    return 


def deleteFromCalcServerByMonth(outfname):
    server='172.32.16.136'
    user='ec2-user'
    k = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/markskey.pem'))
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = server, username = user, pkey = k)
    scpcli = SCPClient(c.get_transport())
    scpcli.put(outfname, outfname)
    command = f'cat {outfname} | while read i ; do rm -Rf ~/ukmon-shared/$i ; done > /tmp/{outfname}.log 2>&1'
    stdin, stdout, stderr = c.exec_command(command)
    return 


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Find and clear down historical raw data.")

    arg_parser.add_argument('periods', metavar='PERIODS', nargs='+', type=str,
        help='Period to clear down in yyyymm format.')

    cml_args = arg_parser.parse_args()
    dtstr = cml_args.periods[0]
    print(f'Clearing data for {dtstr}')

    archbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmon-shared')[5:]
    outdir = os.getenv('TMP', default='/tmp')

    mthfiles, outfname = findInputDataByMonth(dtstr, archbucket, outdir)
    deleteS3FilesByMonth(mthfiles, archbucket)
    #deleteFromCalcServerByMonth(outfname)