import sys
import os
import boto3
from wmpl.Utils.Pickling import loadPickle
from traj.pickleAnalyser import createAdditionalOutput


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


def createExtraJpgtxt(outdir, traj, imglistfile):
    _, orbfldr = os.path.split(outdir)
    dtstr=orbfldr[:15].replace('-','_')
    imglist = open(imglistfile, 'r').readlines()
    allimgs = []
    for obs in traj.observations:
        statid = obs.station_id
        allimgs = allimgs + [x for x in imglist if dtstr in x and statid in x]
    if len(allimgs) > 0:
        allimgs = list(dict.fromkeys(allimgs))
        with open(os.path.join(outdir, 'extrajpgs.txt'),'w') as outf:
            for img in allimgs:
                outf.write(img)


def recreateOrbitFiles(outdir, pickname):
    traj = loadPickle(outdir, pickname)
    traj.save_results = True
    print('loaded pickle')
    createAdditionalOutput(traj, outdir)
    print('created additional output')
    basename = pickname[:15]
    repname = basename + '_report.txt'
    traj.saveReport(dirnam, repname, None, False)
    traj.savePlots(dirnam, basename, show_plots=False, ret_figs=False)
    print('created reports and figures')
    orbparent, orbfldr = os.path.split(outdir)
    yr = orbfldr[:4]
    ym = orbfldr[:6]
    ymd = orbfldr[:8]
    print(f'orbit folder is {orbfldr}')

    imgfldr, _ = os.path.split(orbparent)
    imglistfile = os.path.join(imgfldr, f'imglist-{ym}.txt')
    createExtraJpgtxt(outdir, traj, imglistfile)

    files = os.listdir(outdir)
    mdasess = boto3.Session(profile_name='ukmda_admin')
    ukmsess = boto3.Session(profile_name='ukmonshared')
    s3mda = mdasess.client('s3')
    s3ukm = ukmsess.client('s3')
    if int(yr) > 2020: 
        webfldr = f'reports/{yr}/orbits/{ym}/{ymd}'
    else:
        webfldr = f'reports/{yr}/orbits/{ym}'
    for fil in files:
        locfname = f'{outdir}/{fil}'
        if 'summary' in fil or 'extrajpgs.txt' in fil:
            keyname = f"{webfldr}/{orbfldr}/{fil}"
        else:
            keyname = f"{webfldr}/{orbfldr}/{orbfldr[:15]}{fil[15:]}"
        extraargs = getExtraArgs(fil)
        print(f'uploading {keyname}')
        s3mda.upload_file(locfname, 'ukmda-website', keyname, ExtraArgs=extraargs)
        try:
            s3ukm.upload_file(locfname, 'ukmeteornetworkarchive', keyname, ExtraArgs=extraargs)
        except Exception:
            print('unable to push to old website')
        if 'report' in fil or 'pickle' in fil:
            targkey = f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{orbfldr}/{fil}'
            print(f'uploading {targkey}')
            s3mda.upload_file(locfname, 'ukmda-shared', targkey, ExtraArgs=extraargs)
            try:
                s3ukm.upload_file(locfname, 'ukmon-shared', targkey, ExtraArgs=extraargs)
            except Exception:
                print('unable to push to old shared area')


if __name__ == '__main__':
    dirnam, picknam = os.path.split(sys.argv[1])
    recreateOrbitFiles(dirnam, picknam)
