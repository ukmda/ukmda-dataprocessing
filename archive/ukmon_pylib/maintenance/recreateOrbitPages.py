import sys
import os
import boto3
import platform
import datetime
from wmpl.Utils.Pickling import loadPickle, savePickle
from traj.pickleAnalyser import createAdditionalOutput
from boto3.dynamodb.conditions import Key


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


def getImgListFromDdb(pickname):
    sess = boto3.Session(profile_name='ukmonshared')
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    dtstr = pickname[:12]
    table = ddb.Table('live')
    resp = table.query(IndexName='month-image_name-index', 
                        KeyConditionExpression=Key('month').eq(dtstr[4:6]) & Key('image_name').begins_with(f'M{dtstr}'),
                        ProjectionExpression='image_name')
    imglist = []
    if 'Items' in resp:
        for item in resp['Items']:
            imglist.append(item['image_name'])
    return imglist


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


def fixupTrajComments(traj, availableimages, outdir, picklename, yr, ym):
    s3 = boto3.client('s3')
    madeupdate = False
    for obs in traj.observations:
        pickdtstr = picklename[:15]
        pickdt = datetime.datetime.strptime(pickdtstr, '%Y%m%d_%H%M%S')
        if obs.comment is None:
            relevantimages = [x for x in availableimages if obs.station_id in x]
            for img in relevantimages:
                dtstr = img[1:15]
                camid = obs.station_id
                ff_name = f'img/single/{yr}/{ym}/FF_{camid}_{dtstr}'
                flist = s3.list_objects_v2(Bucket='ukmda-website', Prefix=ff_name)
                comment = ''
                if 'Contents' in flist:
                    for fl in flist['Contents']:
                        key = fl['Key']
                        key = key[key.find('FF_'):]
                        keydt = datetime.datetime.strptime(key[10:25], '%Y%m%d_%H%M%S')
                        if (pickdt - keydt).seconds < 11:
                            comment = f'{{"ff_name": "{key}"}}'
                #print(img, comment)
            print(f'updated comment to {comment} for {obs.station_id}')
            obs.comment = comment
            madeupdate = True
    if madeupdate:
        savePickle(traj, outdir, picklename)
    return


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
    traj.saveReport(outdir, repname, None, False)
    traj.savePlots(outdir, basename, show_plots=False, ret_figs=False)
    print('created reports and figures')
    orbparent, orbfldr = os.path.split(outdir)
    yr = orbfldr[:4]
    ym = orbfldr[:6]
    ymd = orbfldr[:8]
    print(f'orbit folder is {orbfldr}')

    availableimages = getImgListFromDdb(pickname)
    createExtraJpgtxt(outdir, traj, availableimages)
    createExtraJpgHtml(outdir, orbparent, yr, ym)
    fixupTrajComments(traj, availableimages, outdir, pickname, yr, ym)

    if doupload:
        files = os.listdir(outdir)
        mdasess = boto3.Session(profile_name='ukmda_admin')
        s3mda = mdasess.client('s3')
        if int(yr) > 2020: 
            webfldr = f'reports/{yr}/orbits/{ym}/{ymd}'
        else:
            webfldr = f'reports/{yr}/orbits/{ym}'
        for fil in files:
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
