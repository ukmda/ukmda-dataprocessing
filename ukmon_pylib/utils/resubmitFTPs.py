# resubmit missed ftpdetect files

import os
import sys
import shutil
import glob
import datetime

import fileformats.CameraDetails as cd


def resubmitFTPs(dt):
    dtstr = dt.strftime('%Y/%Y%m/%Y%m%d')
    archdir = os.getenv('ARCHDIR', default='/home/ec2-user/ukmon-shared/archive')

    cinfo = cd.SiteInfo()
    cams = cinfo.getAllCamsAndFolders(isactive=True)

    for cam, fldr in zip(cams[0], cams[1]):
        targfldr = f'{archdir}/{fldr}/{dtstr}'
        ftps = glob.glob1(targfldr, 'FTPdetect*.txt')
        if len(ftps) == 0:
            print(f'no ftpdetect in {targfldr}')
            continue
        ftpfile = os.path.join(targfldr, ftps[0])
        tmpfile = os.path.join('/tmp', ftps[0])
        print(cam, ftps[0])
        shutil.copyfile(ftpfile, tmpfile)
        shutil.copyfile(tmpfile, ftpfile)

    return


if __name__ == '__main__':
    dt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    resubmitFTPs(dt)
