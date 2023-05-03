# Copyright (C) 2018-2023 Mark McIntyre
#
# python script to get all live JPGs for a specified time
#
import os
import sys
import boto3
import datetime
import pandas as pd
import requests


def getLiveJpgs(dtstr, outdir=None, create_txt=False):
    """
    Retrieve live images from the ukmon website that match a pattern  

    Arguments:  
        dtstr:      [str] Date in YYYYMMDD_HHMMSS format. Partial strings allowed  
        outdir:     [str] Where to save the file. Default is to create a folder named dtstr  
        create_txt: [bool] If true, create a text file containing the pattern matches  

    Notes:  
        We only keep the last few thousand live images so this function will return nothing
        for older data. 
    """
    if outdir is None:
        outdir = dtstr
    os.makedirs(outdir, exist_ok=True)

    apiurl = 'https://api.ukmeteornetwork.co.uk/liveimages/getlive'
    liveimgs = pd.read_json(f'{apiurl}?pattern={dtstr}')

    weburl = 'https://live.ukmeteornetwork.co.uk/'

    for _, img in liveimgs.iterrows():
        try:
            jpgurl = f'{weburl}{img.image_name}'
            _download(jpgurl, outdir)
            xmlurl = jpgurl.replace('P.jpg', '.xml')
            _download(xmlurl, outdir)
            print(f'retrieved {jpgurl}')
            if create_txt:
                _createTxtFile(img.image_name, outdir)
        except:
            print(f'{img.image_name} unavailable')


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


def _createTxtFile(fname, outdir='.'):
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


def _download(url, outdir):
    get_response = requests.get(url, stream=True)
    file_name = url.split("/")[-1]
    with open(os.path.join(outdir, file_name), 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=4096):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


if __name__ == '__main__':
    getLiveJpgs(sys.argv[1])
