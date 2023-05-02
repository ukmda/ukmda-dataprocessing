# Copyright (C) 2018-2023 Mark McIntyre
#
# python script to get all live JPGs for a specified time
#
import os
import sys
import boto3
import datetime
from ukmon_meteortools.fileformats import ReadUFOCapXML as ufoc


def getLiveJpgs(dtstr, outdir=None, create_txt=False, buck_name=None):
    """
    Retrieve live images from the ukmon website that match a pattern  

    Arguments:  
        dtstr:      [str] Date in YYYYMMDD_HHMMSS format. Partial strings allowed  
        outdir:     [str] Where to save the file. Default is to create a folder named dtstr  
        create_txt: [bool] If true, create a text file containing the pattern matches  
        buck_name:  [str] S3 bucket to read. Default ukmon-live.   

    Notes:  
        This function will fail if you do not have access to the bucket.   
    """
    if outdir is None:
        outdir = dtstr
    os.makedirs(outdir, exist_ok=True)
    if buck_name is None:
        buck_name = os.getenv('UKMONLIVEBUCKET', default='s3://ukmon-live')[5:]
    s3 = boto3.client('s3')
    print(f'looking for {dtstr} in {buck_name}')
    try:
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=f'M{dtstr}')
        if x['KeyCount'] > 0:
            print(f"found {x['KeyCount']} records, saving to {outdir}")
            for k in x['Contents']:
                key = k['Key']
                if '.xml' in key:
                    s3.download_file(buck_name, key, os.path.join(outdir, key))
                    x = ufoc.UCXml(os.path.join(outdir, key))
                    fn = x.ucxml['ufocapture_record']['@cap'].strip()
                    os.remove(os.path.join(outdir, key))
                    key = key.replace('.xml', 'P.jpg')
                    if len(fn) < 5:
                        outkey = key
                        #spls = key.split('_')
                        #stationid = spls[-1][:6].lower()
                        #dtime = key[1:16]
                        #patt = f'FF_{stationid}_{dtime}'
                    else:
                        outkey = fn.replace('.fits', '.jpg')
                        #patt = fn[:26]
                        #stationid = fn[3:9].lower()
                    print(key)
                    s3.download_file(buck_name, key, os.path.join(outdir, outkey))
                    if create_txt is True:
                        createTxtFile(key, outdir)
        else:
            print('no records found')
    except:
        print('Error accessing AWS S3 - do you have access?')


def getFBFiles(patt, outdir='.'):
    """
    Retrieve fireball files from the ukmon website that match a pattern

    Arguments:
        patt:      [str] pattern to match
        outdir:     [str] Where to save the file. Default is '.''

    Notes:
        This function will fail if you do not have access to the ukmon-shared bucket. 
    """
    buck_name = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmon-shared')[5:]
    s3 = boto3.client('s3')
    print(f'looking for {patt} in {buck_name}')
    fullpatt = f'fireballs/interesting/{patt}'
    try:
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                _, fname = os.path.split(key)
                print(f"saving {fname} to {outdir.lower()}")
                s3.download_file(buck_name, key, os.path.join(outdir, fname))
        # platepar file
        _, camid = os.path.split(outdir)
        fullpatt = f'consolidated/platepars/{camid}'
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                fname = 'platepar_cmn2010.cal'
                print(f"saving {fname} to {outdir.lower()}")
                s3.download_file(buck_name, key, os.path.join(outdir, fname))
        # config file
        dtstr = patt[10:25]
        gotcfg = False
        fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr[:8]}'
        x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
        if x['KeyCount'] > 0:
            for k in x['Contents']:
                key = k['Key']
                fname = '.config'
                if fname in key:
                    print(f"saving {fname} to {outdir.lower()}")
                    s3.download_file(buck_name, key, os.path.join(outdir, fname))
                    gotcfg = True
        if gotcfg is False:
            dt = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
            dtstr = (dt +datetime.timedelta(days = -1)).strftime('%Y%m%d_%H%M%S')
            fullpatt = f'matches/RMSCorrelate/{camid}/{camid}_{dtstr[:8]}'
            x = s3.list_objects_v2(Bucket=buck_name,Prefix=fullpatt)
            if x['KeyCount'] > 0:
                for k in x['Contents']:
                    key = k['Key']
                    fname = '.config'
                    if fname in key:
                        print(f"saving {fname} to {outdir.lower()}")
                        s3.download_file(buck_name, key, os.path.join(outdir, fname))
                        gotcfg = True
    except:
        print('Error accessing AWS S3 - do you have access?')
    return 


def createTxtFile(fname, outdir='.'):
    """
    Create a text file named after the cameraID, containing a list of fireball files 
    to be retrieved from a remote camera

    Arguments:
        fname:  [str] the name of the FF file to be retrieved
        outdir: [str] where to save the files. Default '.'

    Notes:
        the fname parameter should be the name of the live JPG for which you wish to 
        retrieve the corresponding FF and FR files.
    """
    if fname[0] == 'M':
        spls = fname.split('_')
        stationid = spls[-1][:6].lower()
        dtime = fname[1:16]
        patt = f'FF_{stationid}_{dtime}'
        stationid = stationid.lower()
    else:
        patt = fname[:25]
        stationid = fname[3:9].lower()
    txtf = os.path.join(outdir, f'{stationid}.txt')
    if os.path.isfile(txtf):
        os.remove(txtf)
    patt = patt.upper()
    with open(txtf,'w') as outf:
        outf.write(f'{patt}\n{patt.replace("FF_", "FR_")}\n')
    return txtf


if __name__ == '__main__':
    getLiveJpgs(sys.argv[1])
