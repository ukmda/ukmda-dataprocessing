# powershell script to get test data for the Max Cam process

import os
import sys
import boto3
import fileformats.extractRawDataOneEvent as erdv


def gatherData(camlist, ymd, outdir, patt):
    s3bucket='ukmon-shared'
    s3 = boto3.resource('s3')

    for camid in camlist:
        pref = f'matches/RMSCorrelate/{camid}/{camid}_{ymd}'
        for _, obj in enumerate(s3.Bucket(s3bucket).objects.filter(Prefix=pref)):
            fldr = obj.key.split('/')[3].strip()
            os.makedirs(os.path.join(outdir, camid, fldr), exist_ok=True)
            localf = os.path.basename(obj.key)
            if f'FTPdetectinfo_{fldr}.txt' in obj.key:
                localftpname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, localftpname)
            elif 'platepars_all_recalibrated.json' in obj.key:
                ppname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, ppname)
            elif '.config' in obj.key:
                cfgname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, cfgname)

    for camid in camlist:
        if os.path.isdir(os.path.join(outdir, camid)):
            dirs = os.listdir(os.path.join(outdir, camid))
            fils = os.listdir(os.path.join(outdir, camid, dirs[0]))
            ftpfile = [f for f in fils if 'FTP' in f and 'old' not in f and 'new' not in f]
            localftpfile = os.path.join(outdir, camid, dirs[0], ftpfile[0])
            erdv.filterFTPforSpecificTime(localftpfile, patt)


if __name__ == '__main__':
    camlist = ['UK000S','UK0006','UK0035','UK003C','UK003D','UK0069', 
            'UK006S','UK0070','UK007A','UK007H','UK007L','UK007Q']
    dtstr = '20230112'
    patt = '20230113_021451'

    gatherData(camlist, dtstr, 'MaxCams', patt)
