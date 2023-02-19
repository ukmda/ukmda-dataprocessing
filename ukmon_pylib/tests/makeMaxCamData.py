# powershell script to get test data for the Max Cam process

import os
import sys
import boto3


camlist = ['UK000S','UK0006','UK0035','UK003C','UK003D','UK0069', 
           'UK006S','UK0070','UK007A','UK007H','UK007L','UK007Q']
dtstr = '20230112'


def gatherData(camlist, ymd, outdir):
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
                ppname = os.path.join(outdir, camid, fldr, localf)
                s3.meta.client.download_file(s3bucket, obj.key, ppname)


if __name__ == '__main__':
    gatherData(camlist, dtstr, 'MaxCams')
