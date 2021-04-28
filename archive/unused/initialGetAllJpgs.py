# python routine to move A.XML files to a single location

import boto3
import csv
import sys
import os
import configparser as cfg


def getCameraDetails():
    # fetch camera details from the CSV file
    fldrs = []
    cams = []
    lati = []
    alti = []
    longi = []
    camtyp = []
    fullcams = []
    camfile = 'camera-details.csv'

    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + camfile, camfile)
    with open(camfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0][:1] != '#':
                if row[1] == '':
                    fldrs.append(row[0])
                else:
                    fldrs.append(row[0] + '/' + row[1])
                if int(row[11]) == 1:
                    cams.append(row[2] + '_' + row[3])
                else:
                    cams.append(row[2])
                fullcams.append(row[0] + '_' + row[3])
                longi.append(float(row[8]))
                lati.append(float(row[9]))
                alti.append(float(row[10]))
                camtyp.append(int(row[11]))
    os.remove(camfile)
    return cams, fldrs, lati, longi, alti, camtyp, fullcams


def getMonth(yymm, target):
    s3 = boto3.client('s3')
    s3r = boto3.resource('s3')
    locs, cams, _, _, _, typ, _ = getCameraDetails()
    yy = yymm[:4]
    for cam in cams:
        pathstr = 'archive/' + cam + '/' + yy + '/' +yymm + '/'
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket='ukmon-shared', Prefix=pathstr)
        for page in pages:
            if page.get('Contents',None):
                for obj in page['Contents']:
                    if 'P.jpg' in obj['Key']:
                        s3object = obj['Key']
                        x = s3object.find('M20')
                        outf = 'img/single/{:s}/{:s}/{:s}'.format(yy, yymm, s3object[x:])
                        print(s3object, outf)
                        src = {'Bucket': 'ukmon-shared', 'Key': obj['Key']}
                        s3r.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src,
                            ContentType="image/jpeg", MetadataDirective='REPLACE')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: python initialGetAllJpgs.py configfile yyyymm')
    else:
        config=cfg.ConfigParser()
        config.read(sys.argv[1])
        target = config['config']['WEBSITEBUCKET']
        target = target[5:]
        getMonth(sys.argv[2], target)
