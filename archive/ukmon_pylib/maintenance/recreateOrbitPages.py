import sys
import os
import boto3
import platform
from wmpl.Utils.Pickling import loadPickle, savePickle
from traj.pickleAnalyser import createAdditionalOutput
import requests
import datetime
import json


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


def getImgList(outdir, traj):
    if os.path.isdir(os.path.join(outdir, '..', 'jpgs')):
        imglist = os.listdir(os.path.join(outdir, '..', 'jpgs'))
        return imglist
    orbname=traj.output_dir.replace('\\','/').split('/')[-1]
    if orbname == '.':
        orbname = os.path.split(outdir)[1]
    testdt = datetime.datetime.strptime(orbname.replace('-','_')[:15], '%Y%m%d_%H%M%S')
    testdt = testdt + datetime.timedelta(seconds=-10)
    dtstr = testdt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    dtstr2 = (testdt + datetime.timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    apiurl = 'https://api.ukmeteors.co.uk/liveimages/getlive'
    apiurl = f'{apiurl}?dtstr={dtstr}&enddtstr={dtstr2}&fmt=trueimg'
    res = requests.get(apiurl)
    if res.status_code == 200:
        jsondata = json.loads(res.text)
        return jsondata['images']
    else:
        return []


def createExtraJpgtxt(outdir, traj, availableimages):
    _, orbfldr = os.path.split(outdir)
    dtstr=orbfldr[:15].replace('-','_')
    allimgs = []
    for obs in traj.observations:
        statid = obs.station_id
        allimgs = allimgs + [x for x in availableimages if dtstr in x and statid in x]
    if len(allimgs) > 0:
        allimgs = list(dict.fromkeys(allimgs))
        with open(os.path.join(outdir, 'extrajpgs.txt'),'w') as outf:
            for img in allimgs:
                outf.write(img)


def createExtraJpgHtml(outdir, parentfldr, yr, ym):
    mdasess = boto3.Session(profile_name='ukmda_admin')
    s3mda = mdasess.client('s3')
    webfldr = f'img/single/{yr}/{ym}'
    with open(os.path.join(outdir, 'extrajpgs.html'), 'w') as outf:
        jpgfldr = os.path.join(parentfldr, 'jpgs')
        if os.path.isdir(jpgfldr):
            jpgs = os.listdir(jpgfldr)
            for jpg in jpgs:
                li = f"<a href=\"/img/single/{yr}/{ym}/{jpg}\"><img src=\"/img/single/{yr}/{ym}/{jpg}\" width=\"20%\"></a>\n"
                outf.write(li)
                locfname = f'{jpgfldr}/{jpg}'
                keyname = f'{webfldr}/{jpg}'
                s3mda.upload_file(locfname, 'ukmda-website', keyname, ExtraArgs=getExtraArgs(jpg))
    webfldr = f'img/mp4/{yr}/{ym}'
    with open(os.path.join(outdir, 'extrampgs.html'), 'w') as outf:
        jpgfldr = os.path.join(parentfldr, 'mp4s')
        if os.path.isdir(jpgfldr):
            jpgs = os.listdir(jpgfldr)
            for jpg in jpgs:
                li = f"<a href=\"/img/mp4/{yr}/{ym}/{jpg}\"><video width=\"20%\"><source src=\"/img/mp4/{yr}/{ym}/{jpg}\" width=\"20%\" type=\"video/mp4\"></video></a>\n"
                outf.write(li)
                locfname = f'{jpgfldr}/{jpg}'
                keyname = f'{webfldr}/{jpg}'
                s3mda.upload_file(locfname, 'ukmda-website', keyname, ExtraArgs=getExtraArgs(jpg))


def fixupTrajComments(traj, availableimages, outdir, picklename):
    s3 = boto3.client('s3')
    madeupdate = False
    camcount = 0
    prevcamid = ''
    for obs in traj.observations:
        camid = obs.station_id
        if obs.comment is None or len(obs.comment) < 5:
            #print(prevcamid, camid)
            if prevcamid != camid[:6]:
                camcount = 0
            statimages = [x for x in availableimages if camid in x]
            #print(camid, camcount, statimages)
            if len(statimages) == 0:
                continue
            img = statimages[camcount]
            if len(statimages) > 1:
                camcount += 1
            else:
                camcount = 0
            comment = ''
            if img[0]=='M':
                dtstr = img[1:15]
                ff_name = f'img/single/{dtstr[:4]}/{dtstr[:6]}/FF_{camid}_{dtstr}'
            else:
                dtstr = img[10:25]
                ff_name = f'img/single/{dtstr[:4]}/{dtstr[:6]}/{img}'
            flist = s3.list_objects_v2(Bucket='ukmda-website', Prefix=ff_name)
            if 'Contents' in flist:
                comment = f'{{"ff_name": "{img}"}}'
                print(f'updated comment to {comment} for {obs.station_id}')
            obs.comment = comment
            madeupdate = True
        prevcamid = camid[:6]
    if madeupdate:
        savePickle(traj, outdir, picklename)
    return


def checkIfFileNeeded(filename):

    # update this if there's an additional file created by WMPL that we want
    # to use on the website
    # NB THIS ALSO HAS TO BE CHANGED in TRAJSOLVER if more files needed
    if 'orbit_top.png' in filename or 'orbit_side.png' in filename or 'ground_track.png' in filename:
        return True
    if 'velocities.png' in filename or 'lengths.png' in filename or 'lags_all.png' in filename:
        return True
    if 'abs_mag.png' in filename or 'abs_mag_ht.png' in filename or 'report.txt' in filename:
        return True
    if 'all_angular_residuals.png' in filename or 'all_spatial_total_residuals_height.png' in filename:
        return True
    if 'trajectory.pickle' in filename:
        return True
    if 'extra' in filename: 
        return True
    return False


def recreateOrbitFiles(outdir, pickname, doupload=False):
    traj = loadPickle(outdir, pickname)
    traj.save_results = True
    # need to add the enable_OSM_plot attribute if its missing
    if not hasattr(traj,'enable_OSM_plot'):
        traj.enable_OSM_plot = True
        savePickle(traj, outdir, pickname)
    print('loaded pickle')
    if platform.node() == 'MARKSDT':
        createAdditionalOutput(traj, outdir)
        print('created additional output')
    basename = pickname[:15]
    repname = basename + '_report.txt'
    try: 
        traj.saveReport(outdir, repname, None, False)
        traj.savePlots(outdir, basename, show_plots=False, ret_figs=False)
    except:
        print('unable to process pickle properly')
        pass
    print('created reports and figures')
    orbparent, orbfldr = os.path.split(outdir)
    yr = orbfldr[:4]
    ym = orbfldr[:6]
    ymd = orbfldr[:8]
    print(f'orbit folder is {orbfldr}')

    availableimages = getImgList(outdir, traj)
    createExtraJpgtxt(outdir, traj, availableimages)
    createExtraJpgHtml(outdir, orbparent, yr, ym)
    try:
        fixupTrajComments(traj, availableimages, outdir, pickname)
    except:
        print('unable to fixup traj comments')
        pass
    

    if doupload:
        files = os.listdir(outdir)
        mdasess = boto3.Session(profile_name='ukmda_admin')
        s3mda = mdasess.client('s3')
        if int(yr) > 2020: 
            webfldr = f'reports/{yr}/orbits/{ym}/{ymd}'
        else:
            webfldr = f'reports/{yr}/orbits/{ym}'
        for fil in files:
            if not checkIfFileNeeded(fil):
                print(f'skipping {fil}')
                continue
            locfname = f'{outdir}/{fil}'
            if 'summary' in fil or 'extrajpgs.txt' or 'html' in fil:
                keyname = f"{webfldr}/{orbfldr}/{fil}"
            else:
                keyname = f"{webfldr}/{orbfldr}/{orbfldr[:15]}{fil[15:]}"
            extraargs = getExtraArgs(fil)
            print(f'uploading {keyname}')
            s3mda.upload_file(locfname, 'ukmda-website', keyname, ExtraArgs=extraargs)
            if 'report' in fil or 'pickle' in fil:
                targkey = f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{orbfldr}/{fil}'
                print(f'uploading {targkey}')
                s3mda.upload_file(locfname, 'ukmda-shared', targkey, ExtraArgs=extraargs)
    return 


if __name__ == '__main__':
    dirnam, picknam = os.path.split(sys.argv[1])
    doupload = False
    if len(sys.argv) > 2: 
        doupload = True
    if '-' in dirnam:
        newdirnam = dirnam[:-3].replace('-','_') + '_UK'
        os.rename(dirnam, newdirnam)
        recreateOrbitFiles(newdirnam, picknam, doupload)
    else:
        recreateOrbitFiles(dirnam, picknam, doupload)
