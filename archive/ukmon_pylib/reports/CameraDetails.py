# Create a data type for the camera location details
# Copyright (C) 2018-2023 Mark McIntyre
import os
import glob 
import json
import pandas as pd 
import boto3

'''
creating and managing the more-accurate camera location info
'''


def getCamLocDirFov(camid, datadir=None):
    if datadir is None:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    camdb = json.load(open(os.path.join(datadir, 'admin', 'cameraLocs.json')))
    if camid not in camdb.keys():
        return False
    return camdb[camid]


def updateCamLocDirFovDB(datadir=None):
    if datadir is None:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    camdb = {}
    ppfiles = glob.glob(os.path.join(datadir, 'consolidated','platepars', '*.json'))
    for ppf in ppfiles:
        try:
            pp = json.load(open(ppf))
            camid = pp['station_code']
            camdb.update({camid: {'lat': pp['lat'], 'lon': pp['lon'], 'ele': pp['elev'],
                'az': pp['az_centre'], 'alt': pp['alt_centre'], 'fov_h': pp['fov_h'], 'fov_v': pp['fov_v'], 
                'rot': pp['rotation_from_horiz']}})
        except:
            # platepar was malformed
            continue
    with open(os.path.join(datadir, 'admin', 'cameraLocs.json'), 'w') as outf:
        json.dump(camdb, outf, indent=4)


def loadLocationDetails(table='camdetails', ddb=None, loadall=False):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table(table)
    res = table.scan()
    # strictly, should check for LastEvaluatedKey here, in case there was more than 1MB of data,
    # however that equates to around 30,000 users which i hope we never have... 
    values = res.get('Items', [])
    camdets = pd.DataFrame(values)
    camdets.sort_values(by=['stationid'], inplace=True)
    if not loadall:
        camdets.dropna(inplace=True, subset=['eMail','humanName','site'])
    camdets['camtype'] = camdets['camtype'].astype(int)
    camdets['active'] = camdets['active'].astype(int)
    return camdets


def findLocationInfo(srchstring, ddb=None, statdets=None):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    s1 = statdets[statdets.stationid.str.contains(srchstring)]
    s2 = statdets[statdets.eMail.str.contains(srchstring)]
    s3 = statdets[statdets.humanName.str.contains(srchstring)]
    s4 = statdets[statdets.site.str.contains(srchstring)]
    srchres = pd.concat([s1, s2, s3, s4])
    srchres.drop(columns=['oldcode','active','camtype'], inplace=True)
    return srchres


def createCDCsv(targetloc):
    sess = boto3.Session(profile_name='ukmonshared')
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    camdets = loadLocationDetails(ddb=ddb)
    cd4csv = camdets[['site','stationid','oldcode','direction','camtype','active']]
    pd.options.mode.chained_assignment = None
    cd4csv['dummycode'] = camdets.stationid
    pd.options.mode.chained_assignment = 'warn'
    cd4csv = cd4csv[['site','stationid','oldcode','direction','camtype','dummycode','active']]
    cd4csv = cd4csv.rename(columns={'stationid':'camid', 'oldcode':'lid', 'direction':'sid'})
    cd4csv.sort_values(by=['active','camid'], inplace=True)
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    outfname = os.path.join(datadir, targetloc, 'camera-details.csv')
    cd4csv.to_csv(outfname, index=False)
    with open(os.path.join(datadir, 'activecamcount.txt'), 'w') as outf:
        outf.write(str(len(cd4csv[cd4csv.active==1])))
    createStatOptsHtml(camdets, datadir)
    createStatOptsHtml(camdets, datadir, True)
    createStatOptsHtml(camdets, datadir, True, True)
    return


def createStatOptsHtml(sitedets, datadir, active=False, locs=False):
    """
    Create an HTML file containing a list of stations or locations
    These files are used by the website search functions
    """
    if active:
        if locs:
            siteidx = os.path.join(datadir, 'activestatlocs.html')  
            sitedets = sitedets.sort_values(by=['site', 'stationid'])
        else:
            siteidx = os.path.join(datadir, 'activestatopts.html')  
        sitedets = sitedets[sitedets.active==1]
    else:
        siteidx = os.path.join(datadir, 'statopts.html')  
    with open(siteidx, 'w') as outf:
        if not active:
            outf.write('<label for="statselect">Station</label>\n')
            outf.write('<select class="bootstrap-select" id="statselect">\n')
        outf.write('<option value="1" selected="selected">All</option>\n')
        rowid = 2
        for _, rw in sitedets.iterrows():
            if locs:
                cam = f'{str(rw.site)}/{str(rw.stationid)}'
            else:
                cam = str(rw.stationid)
            outf.write(f'<option value="{rowid}">{cam}</option>\n')
            rowid += 1
        if not active:
            outf.write('</select>\n')
    return 


def findSite(stationid, camdets=None, ddb=None):
    if camdets is None:
        camdets = loadLocationDetails(ddb=ddb) 
    cc = camdets[camdets.stationid==stationid]
    if len(cc) > 0:
        res = cc.iloc[0]['site']
    else:
        res = 'Unknown'
    return res


def findEmail(stationid, camdets=None, ddb=None):
    if camdets is None:
        camdets = loadLocationDetails(ddb=ddb) 
    cc = camdets[camdets.stationid==stationid]
    if len(cc) > 0:
        res = cc.iloc[0]['eMail']
    else:
        res = 'Unknown'
    return res
