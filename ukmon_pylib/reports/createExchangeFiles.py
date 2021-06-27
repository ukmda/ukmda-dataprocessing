import fileformats.UAFormats as uaf 
import fileformats.CameraDetails as cdd
import datetime
import os
import sys
import shutil
import configparser as cfg


def createDetectionsFile(sDate, datadir, nolatest=False):
    # read and process the daily event data
    dets=uaf.DetectedCsv(os.path.join(datadir,'UKMON-all-single.csv'))
    data = dets.getExchangeData(sDate)
    
    outfname = os.path.join(datadir, 'browse/daily/ukmon-{}.csv'.format(sDate.strftime('%Y%m%d')))
    with open(outfname,'w') as outf:
        outf.write('camera_id,datetime,image_URL\n')
        for li in data:
            outf.write(li[0] + ',' + li[1] + ',\n')
    if nolatest is False: 
        lfname = os.path.join(datadir, 'browse/daily/ukmon-latest.csv')
        shutil.copy(outfname, lfname)
    return


def createMatchesFile(sDate, datadir, nolatest=False):
    # read and process the daily event data
    dets=uaf.DetectedCsv(os.path.join(datadir,'UKMON-all-single.csv'))
    data = dets.getExchangeData(sDate)
    
    outfname = os.path.join(datadir, 'browse/daily/ukmon-{}.csv'.format(sDate.strftime('%Y%m%d')))
    with open(outfname,'w') as outf:
        outf.write('camera_id,datetime,image_URL\n')
        for li in data:
            outf.write(li[0] + ',' + li[1] + ',\n')
    if nolatest is False: 
        lfname = os.path.join(datadir, 'browse/daily/ukmon-latest.csv')
        shutil.copy(outfname, lfname)
    return


def createWebpage(datadir):
    idxfile = os.path.join(datadir, 'browse/daily/browselist.js')
    with open(idxfile, 'w') as outf:
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = "h4";\n')

        outf.write('var row = table.insertRow(-1);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "<a href=./ukmon-latest.csv>ukmon-latest.csv</a>";\n')

        outf.write('var row = table.insertRow(-1);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "<a href=./cameradetails.csv>cameradetails.csv</a>";\n')

        outf.write('var row = header.insertRow(0);\n')
        outf.write('var cell = row.insertCell(0);\n')
        outf.write('cell.innerHTML = "File";\n')
        outf.write('cell.className = "small";\n')

        outf.write('var outer_div = document.getElementById("browselist");\n')
        outf.write('outer_div.appendChild(table);\n')

        outf.write('})\n')

    return 


def createCameraFile(datadir, nolatest=True):
    camdets = cdd.SiteInfo()
    acs = camdets.getActiveCameras()
    acs = acs[acs['camtyp']==2]
    with open(os.path.join(datadir, 'browse/daily/cameradetails.csv'), 'w') as outf:
        outf.write('camera_id,obs_latitude,obs_longitude,obs_az,obs_ev,obs_rot,fov_horiz,fov_vert\n')
        for li in acs:
            outf.write('{},{:.1f},{:.1f},,,,,\n'.format(li['CamID'].decode('utf-8'), li['Lati'], li['Longi']))
    return


def uploadFiles(config):
    datadir = config['config']['datadir']
    bucket = config['config']['websitebucket']
    keyf = config['config']['websitekey']
    cmd = 'source {} && aws s3 sync {}/browse/daily/ {}/browse/daily/'.format(keyf, datadir, bucket)
    os.system(cmd)
    return


if __name__ == '__main__':
    cfgdir = os.getenv('CONFIG')
    config = cfg.ConfigParser()
    config.read(os.path.join(cfgdir, 'config.ini'))
    datadir = config['config']['datadir']
    if len(sys.argv) > 1:
        targdate = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        nolatest = True
    else:
        targdate = datetime.datetime.now()
        nolatest = False
        createCameraFile(datadir)
    
    createDetectionsFile(targdate, datadir, nolatest)
    #createMatchesFile(targdate, datadir, nolatest)
    createWebpage(datadir)
    uploadFiles(config)
