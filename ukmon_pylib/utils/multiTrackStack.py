# python script to call TrackStack to stack several nights/cameras

#import boto3
#import argparse
import os
import sys
import glob
import datetime
from Utils.TrackStack import trackStack
import RMS.ConfigReader as cr


def multiTrackStack(camlist, start, end, outdir=None, shwr=None):
    locfld = os.getenv('LOCALFOLDER', default='f:/videos/meteorcam/fireballs')
    datadir, _ = os.path.split(locfld)
    if outdir is None:
        outdir = '.'
    print(f'stacking {camlist} for dates {start},{end}, reading from {datadir}, saving to {outdir}')

    sdt = datetime.datetime.strptime(start, '%Y%m%d')
    edt = datetime.datetime.strptime(end, '%Y%m%d')
    d = sdt
    dir_paths = []
    while d <= edt:
        dtstr = d.strftime('%Y%m%d')
        for cam in camlist:
            cam = cam.upper()
            camdir = os.path.join(datadir, cam, 'ConfirmedFiles')
            dirs = glob.glob1(camdir, f'{cam}_{dtstr}*')
            if len(dirs) > 0: 
                srcdir = os.path.join(camdir, dirs[0])
                ftpdet = os.path.join(srcdir, f'FTPdetectinfo_{dirs[0]}.txt')
                if os.path.isfile(ftpdet):
                    print(f'using {ftpdet}')
                    dir_paths.append(srcdir)
        d = d + datetime.timedelta(days=1)

    config = cr.loadConfigFromDirectory('.config', dir_paths[0])
    if shwr is not None:
        shwr = [shwr]

    trackStack(dir_paths, config, border=5, background_compensation=True, 
        hide_plot=False, showers=shwr, darkbackground=False, out_dir=outdir)

    return


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python -m utils.multiTrackStack cam1,cam2,camN yyyymmdd,yyyymmdd [shwr] [outdir]')
        print('use ALL for shower, if you want to also use outdir')
        exit(1)

    if ',' in sys.argv[1]:
        cams = sys.argv[1].split(',')
    else:
        cams = [sys.argv[1]]
    if ',' in sys.argv[2]:
        start, end = sys.argv[2].split(',')
    else:
        start = sys.argv[2]
        end = start
    shwr = None
    if len(sys.argv) > 3:
        shwr = sys.argv[3]
        if shwr == 'ALL':
            shwr = None 
    outdir = '.'
    if len(sys.argv) > 4:
        outdir = sys.argv[4]
    multiTrackStack(cams, start, end, outdir, shwr)
