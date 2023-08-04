# Copyright (C) 2018-2023 Mark McIntyre
#
# lambda function to be triggered when a jpg file arrives in the shared bucket
# to copy it to the archive website
#
import boto3
import os
import sys
import math
from urllib.parse import unquote_plus


def copyJpgToArchive(s3bucket, s3object):
    s3 = boto3.resource('s3')
    target = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')[5:]

    x = s3object.find('M20')
    if x == -1: 
        y = s3object.find('FF_')
        if y == -1:
            if '_stack_'in s3object:
                statid = os.path.basename(s3object)[0:6]
                if statid[0] == '.': 
                    statid = os.path.basename(s3object)[2:8]
                outf = 'latest/{:s}.jpg'.format(statid)
                s3object = unquote_plus(s3object)
                src = {'Bucket': s3bucket, 'Key': s3object}
                print(s3object, outf)
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="image/jpg", MetadataDirective='REPLACE')
                return 
            elif '_calib_report_astrometry' in s3object:
                statid = os.path.basename(s3object)[0:6]
                if statid[0] == '.': 
                    statid = os.path.basename(s3object)[2:8]
                outf = 'latest/{:s}_cal.jpg'.format(statid)
                s3object = unquote_plus(s3object)
                src = {'Bucket': s3bucket, 'Key': s3object}
                print(s3object, outf)
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="image/jpg", MetadataDirective='REPLACE')
                return 
            else:
                return 
        else:
            # its an RMS file probably
            yr = s3object[y+10:y+14]
            ym = s3object[y+10:y+16]
            outf = 'img/single/{:s}/{:s}/'.format(yr, ym) + s3object[y:]
    else:
        # its a UFO file
        print('its a UFO file')
        s3object = unquote_plus(s3object)
        yr = s3object[x+1:x+5]
        ym = s3object[x+1:x+7]
        # read the XML file to get the milliseconds value
        xmlf = s3object[:-5]+'A.XML'
        tmpxml = os.path.join('/tmp', xmlf[x:])
        try: 
            s3.meta.client.download_file(s3bucket, xmlf, tmpxml)
            #print('got xmlfile')
            with open(tmpxml,'r') as inf:
                lis = inf.readlines()
            gotsecs = False
            for li in lis:
                if ' s="' in li:
                    gotsecs = True
                    break
            #print(f'li is {li}')
            if gotsecs is True:
                stn = getStationId(s3object[x+17:])
                ymd_hms = s3object[x+1:x+16]
                secs = li[li.find(' s="')+4:].strip()[:-1]
                msecs = int(math.modf(float(secs))[0]*1000.0)
                newfname = f'FF_{stn}_{ymd_hms}_{msecs:.0f}_0000000.jpg'
                outf = f'img/single/{yr}/{ym}/' + newfname
            else:
                print('unable to find secs value')
                outf = f'img/single/{yr}/{ym}/' + s3object[x:]
        except:
            print('unable to find xml file')
            outf = f'img/single/{yr}/{ym}/' + s3object[x:]

    s3object = unquote_plus(s3object)
    src = {'Bucket': s3bucket, 'Key': s3object}
    print(s3object, outf)
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="image/jpeg", MetadataDirective='REPLACE')

    try:
        s3vid = s3object.replace('.jpg', '.mp4')
        outf = 'img/mp4/{:s}/{:s}/{}'.format(yr, ym, s3vid[y:])
        print(s3vid, outf)
        src = {'Bucket': s3bucket, 'Key': s3vid}
        s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src, ContentType="video/mp4", MetadataDirective='REPLACE')
    except:
        pass
    return


def getStationId(locname):
    if 'Clanfield_NE' in locname:
        return 'UK9990'
    if 'Clanfield_NW' in locname:
        return 'UK9989'
    if 'Clanfield_SE' in locname:
        return 'UK9988'
    return 'UK9999'


def lambda_handler(event, context):

    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    copyJpgToArchive(s3bucket, s3object)


if __name__ == "__main__":
    s3bucket = os.getenv('SHAREDBUCKET', default='s3://ukmda-shared')[5:]
    s3object = 'archive/Tackley/UK0006/2022/202201/20220120/FF_UK0006_20220120_201332_261_0258560.jpg'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if './' in fname:
            s3object = 'archive/' + fname[2:]
        else:
            s3object = 'archive/' + fname
    #print(s3object)
    copyJpgToArchive(s3bucket, s3object)
