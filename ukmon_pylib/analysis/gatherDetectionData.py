#
# Collect data for a potential match at a specific time
#
# 
import os 
import sys
import pandas as pd
from urllib.request import urlretrieve
import requests
import datetime
import boto3


def gatherDetectionData(dttime):
    yr = dttime[:4]
    snglfile = f's3://ukmon-shared/matches/singlepq/singles-{yr}.parquet.gzip'
    cols = ['Filename','ID','Dtstamp','Y']
    sngl = pd.read_parquet(snglfile, columns=cols)
    sngl = sngl[sngl['Y']==int(yr)] # just in case there's some pollution in the database

    fltr = sngl[sngl.Filename.str.contains(dttime)]
    idlist = pd.concat([fltr.ID, fltr.Filename], axis=1).drop_duplicates()
    idlist['Dtstamp'] = [d[10:25] for d in idlist.Filename]
    idlist['Filename']=idlist.Filename.replace('.fits','.jpg', regex=True)
    return idlist


def getJpgs(idlist, outpth):
    for _,row in idlist.iterrows():
        yr = row.Filename[10:14]
        ym = row.Filename[10:16]
        fpth = f'https://archive.ukmeteornetwork.co.uk/img/single/{yr}/{ym}/{row.Filename}'
        outfnam = os.path.join(outpth, row.Filename)
        try:
            urlretrieve(fpth, outfnam)
        except:
            print('unable to get', row.Filename)
            pass
    return


def getECSVfiles(idlist, outpth):
    apiurl = 'https://jpaq0huazc.execute-api.eu-west-1.amazonaws.com/Prod/getecsv?stat={}&dt={}'
    for _,row in idlist.iterrows():
        stat =row.ID
        dts = datetime.datetime.strptime(row.Dtstamp, '%Y%m%d_%H%M%S')
        dt = dts.strftime('%Y-%m-%dT%H:%M:%S')
        res = requests.get(apiurl.format(stat, dt))
        if res.status_code == 200:
            rawdata = res.text
            ecsvlines = rawdata.split('\n') # convert the raw data into a python list
            if len(ecsvlines) > 1:
                numecsvs = len([e for e in ecsvlines if '# %ECSV' in e]) # find out how many meteors 
                # fnamebase = dt.replace(':','_').replace('.','_')+'_UKMON_' +stat  # create an output filename
                # name chosen to match other RMS datafiles
                fnamebase = 'FF_' + stat + '_' + dt.replace(':','_').replace('.','_') +'_UKMON'
                if numecsvs == 1:
                    with open(os.path.join(outpth, fnamebase + '.ecsv'), 'w') as outf:
                        outf.writelines(line + '\n' for line in ecsvlines)
                else:
                    outf = None
                    j=1
                    for i in range(len(ecsvlines)):
                        if '# %ECSV' in ecsvlines[i]:
                            if outf is not None:
                                outf.close()
                                j=j+1
                            outf = open(os.path.join(outpth, fnamebase + '.ecsv'), 'w')
                        outf.write(f'{ecsvlines[i]}\n')
            else:
                print(row.Filename, dt, ecsvlines)
    return 


def getFtpAndPlate(camid, dtstr, tmstr, outdir):
    camdets = pd.read_csv('s3://ukmon-shared/consolidated/camera-details.csv')
    dt = datetime.datetime.strptime(dtstr, '%Y%m%d')
    if int(tmstr) < 1200:
        dt = dt + datetime.timedelta(days = -1)
    site = camdets[camdets.camid == camid].iloc[0].site      
    if site is None:
        print(f'unable to find site for {camid}')
        return 
    tf = camid + '_' + dt.strftime('%Y%m%d') + '_180000'
    targpath = os.path.join(outdir, camid, tf)
    os.makedirs(targpath, exist_ok=True)
    dt2 = dt + datetime.timedelta(days = -1)
    tf2 = camid + '_' + dt2.strftime('%Y%m%d') + '_180000'
    targpath2 = os.path.join(outdir, camid, tf2)
    os.makedirs(targpath2, exist_ok=True)
    yr = dt.year
    ym = dt.strftime('%Y%m')
    ymd = dt.strftime('%Y%m%d')
    srcfldr = f'archive/{site}/{camid}/{yr}/{ym}/{ymd}/'

    s3 = boto3.resource('s3') #,
    #    aws_access_key_id=credentials['AccessKeyId'],
    #    aws_secret_access_key=credentials['SecretAccessKey'],
    #    aws_session_token=credentials['SessionToken'])
    archbucket = 'ukmon-shared'
    for fname in ['platepar_cmn2010.cal','.config','platepars_all_recalibrated.json']:
        locfname = os.path.join(targpath, fname)
        remfname = srcfldr + fname
        try:
            s3.meta.client.download_file(archbucket, remfname, locfname)
        except:
            print(f'unable to download {fname}')
    ftplist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=srcfldr+'FTP') 
    if ftplist['KeyCount'] > 0:
        keys = ftplist['Contents']
        for k in keys:
            fname = k['Key']
            if 'FTPdetectinfo' in fname:
                _, actfname = os.path.split(fname)
                locfname = os.path.join(targpath, actfname)
                s3.meta.client.download_file(archbucket, fname, locfname)
    else:
        print('unable to downlaod FTPdetect file')

    # now change the catalogue entry
    with open(os.path.join(targpath, '.config')) as inf:
        lis = inf.readlines()
    with open(os.path.join(targpath, '.config'),'w') as outf:
        for li in lis:
            li = li.replace('gaia_dr2_mag_11.5.npy', 'BSC5')
            outf.write(li)

    return 


if __name__ == '__main__':
    outpth = f'./{sys.argv[1]}'
    os.makedirs(outpth, exist_ok=True)
    idlist = gatherDetectionData(sys.argv[1])
    getJpgs(idlist, outpth)
    getECSVfiles(idlist, outpth)
    ids = list(idlist.ID)
    with open(os.path.join(outpth, 'ids.txt'), 'w') as outf:
        outf.writelines(line + '\n' for line in ids)

    print(ids)
