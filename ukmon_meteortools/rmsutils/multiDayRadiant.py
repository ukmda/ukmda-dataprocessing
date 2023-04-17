# Copyright (C) 2018-2023 Mark McIntyre

# python script to call TrackStack to stack several nights/cameras

#import boto3
#import argparse
import os
import glob
import datetime
from Utils.ShowerAssociation import showerAssociation
import RMS.ConfigReader as cr
import argparse
import shutil


def multiDayRadiant(camlist, start, end, outdir=None, shwr=None):
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
                    dir_paths.append(ftpdet)
        d = d + datetime.timedelta(days=1)
    cfgdir, _ = os.path.split(dir_paths[0])
    config = cr.loadConfigFromDirectory('.config', cfgdir)

    # file will be created here, need to preserve any existing file then restore afterwards
    targdir, _ = os.path.split(dir_paths[-1])
    prevfiles = glob.glob1(targdir, '*radiants.png')
    if len(prevfiles) > 0:
        if os.path.isfile(os.path.join(targdir, prevfiles[0]+'.tmp')):
            os.remove(os.path.join(targdir, prevfiles[0]+'.tmp'))
        os.rename(os.path.join(targdir, prevfiles[0]), os.path.join(targdir, prevfiles[0]+'.tmp'))
    prevfilestxt = glob.glob1(targdir, '*radiants.txt')
    if len(prevfilestxt) > 0:
        if os.path.isfile(os.path.join(targdir, prevfilestxt[0]+'.tmp')):
            os.remove(os.path.join(targdir, prevfilestxt[0]+'.tmp'))
        os.rename(os.path.join(targdir, prevfilestxt[0]), os.path.join(targdir, prevfilestxt[0]+'.tmp'))

    # Perform shower association
    associations, shower_counts = showerAssociation(config, dir_paths, 
        shower_code=shwr, show_plot=False, save_plot=True, plot_activity=True,
        flux_showers=False, color_map='gist_ncar')

    newn = prevfiles[0]
    if shwr is not None:
        newn = shwr + newn[6:]
    else:
        newn = "ALL" + newn[6:]
    shutil.copyfile(os.path.join(targdir, prevfiles[0]), os.path.join(outdir, newn))
    os.remove(os.path.join(targdir, prevfiles[0]))

    if len(prevfiles) > 0:
        os.rename(os.path.join(targdir, prevfiles[0])+'.tmp', os.path.join(targdir, prevfiles[0]))

    newn = prevfilestxt[0]
    if shwr is not None:
        newn = shwr + newn[6:]
    else:
        newn = "ALL" + newn[6:]

    shutil.copyfile(os.path.join(targdir, prevfilestxt[0]), os.path.join(outdir, newn))
    os.remove(os.path.join(targdir, prevfilestxt[0]))

    if len(prevfilestxt) > 0:
        os.rename(os.path.join(targdir, prevfilestxt[0])+'.tmp', os.path.join(targdir, prevfilestxt[0]))
    return


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description="Perform multiday/camera radiant mapping.")

    arg_parser.add_argument('cams', metavar='CAMS', nargs='+', type=str,
        help='List of cameras, comma-separated.')

    arg_parser.add_argument('dates', metavar='DATES', nargs='+', type=str,
        help='Start and end date, comma-separated in yyyymmdd format.')

    arg_parser.add_argument('-s', '--shower', metavar='SHOWER', type=str,
        help="Associate just this single shower given its code (e.g. PER, ORI, ETA).")

    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', type=str,
        help="Where to save the output file.")

    # Parse the command line arguments
    cml_args = arg_parser.parse_args()
    cams = cml_args.cams[0]
    if ',' in cams:
        cams = cams.split(',')
    else:
        cams = [cams]

    dates = cml_args.dates[0]
    if ',' in dates:
        start, end = dates.split(',')
    else:
        start = dates
        end = start
    
    shwr = None
    if cml_args.shower:
        shwr = cml_args.shower
    
    outdir = '.'
    if cml_args.outdir:
        outdir = cml_args.outdir

    multiDayRadiant(cams, start, end, outdir, shwr)
