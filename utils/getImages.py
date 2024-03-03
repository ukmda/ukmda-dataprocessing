# Copyright Mark McIntyre, 2024-


import os
import sys
import pandas as pd 
import boto3
import requests


def getBrightestSingles(yr, mth, minbri=-1):
    datadir=os.getenv('DATADIR', default='/data3/backups/ukmda/ukmda-shared/matches')
    mf = os.path.join(datadir, 'single', f'singles-{yr}.parquet.snap')
    cols=['Y','M','Mag','Filename']
    singles = pd.read_parquet(mf, columns=cols)
    singles = singles[singles.Y == int(yr)]
    singles = singles[singles.M == int(mth)]
    singles = singles[singles.Mag <= float(minbri)]
    return list(singles.Filename)


def getBrightestMatches(yr, mth, minbri=-1):
    datadir=os.getenv('DATADIR', default='/data3/backups/ukmda/ukmda-shared/matches')
    mf = os.path.join(datadir, 'matched', f'matches-full-{yr}.parquet.snap')
    cols=['_Y_ut','_M_ut','_amag','url']
    singles = pd.read_parquet(mf, columns=cols)
    singles = singles[singles._Y_ut == int(yr)]
    singles = singles[singles._M_ut == int(mth)]
    singles = singles[singles._amag <= float(minbri)]
    return list(singles.url)


def getSingleImages(yr, mth, minbri=-1):
    imglist = getBrightestSingles(yr, mth=mth, minbri=minbri)
    datadir=os.getenv('DATADIR', default='/data3/backups/ukmda/ukmda-shared/matches')
    wsbucket = 'ukmda-website'
    imgdir = os.path.join(datadir, '..','..','images')
    os.makedirs(imgdir, exist_ok=True)
    mp4dir = os.path.join(datadir, '..','..','mp4s')
    os.makedirs(mp4dir, exist_ok=True)
    s3 = boto3.client('s3')
    for img in imglist:
        spls = img.split('_')
        dtstr = spls[2]
        yr = dtstr[:4]
        ym = dtstr[:6]
        img = img.replace('.fits','.jpg')
        srcfile = f'img/single/{yr}/{ym}/{img}'
        trgfldr = f'{imgdir}/{yr}/{ym}'
        os.makedirs(trgfldr, exist_ok=True)
        trgfile = f'{trgfldr}/{img}'
        s3.download_file(wsbucket, srcfile, trgfile)
        img = img.replace('.jpg','.mp4')
        srcfile = f'img/mp4/{yr}/{ym}/{img}'
        trgfldr = f'{mp4dir}/{yr}/{ym}'
        os.makedirs(trgfldr, exist_ok=True)
        trgfile = f'{trgfldr}/{img}'
        try:
            s3.download_file(wsbucket, srcfile, trgfile)
        except Exception:
            pass


def _download(url, outdir, fname=None):
    get_response = requests.get(url, stream=True)
    if fname is None:
        fname = url.split("/")[-1]
    with open(os.path.join(outdir, fname), 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=4096):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return fname


def getMatchImages(yr, mth, minbri=-3):
    datadir=os.getenv('DATADIR', default='/data3/backups/ukmda/ukmda-shared/matches')
    imgdir = os.path.join(datadir, '..','..','imgs')
    ym = f'{yr}{mth:02d}'
    outdir = os.path.join(imgdir, str(yr), ym)
    os.makedirs(outdir, exist_ok=True)
    existingfiles = os.listdir(outdir)
    imglist = getBrightestMatches(yr, mth=mth, minbri=minbri)
    print(f'processing {len(imglist)} matches')
    os.makedirs(imgdir, exist_ok=True)
    for img in imglist:
        img = img.replace('ukmeteornetwork.','ukmeteors.')
        res = requests.get(img)
        lines = res.text.split('\n')
        imglines = [li for li in lines if '.jpg' in li or '.mp4' in li]
        dllist = [im.split('"')[1] for im in imglines]
        for dl in dllist:
            fname = dl.split('/')[-1]
            if fname in existingfiles:
                print(f'skipping {fname}')
            else:
                print(f'getting {fname}')
                if dl[0] !='/':
                    _download(f'https://archive.ukmeteors.co.uk/{dl}', outdir)
                else:
                    _download(f'https://archive.ukmeteors.co.uk{dl}', outdir)
    return imglist


if __name__ == '__main__':
    yr = int(sys.argv[1])
    if len(sys.argv) < 2:
        print('need month')
        exit(0)
    mth = int(sys.argv[2])
    minbri = -3
    if len(sys.argv) > 3:
        minbri = float(sys.argv[3])
    mtchlist = getMatchImages(yr, mth=mth, minbri=minbri)
