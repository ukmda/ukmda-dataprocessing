#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import os
import sys
import json
import datetime
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key

from ftpDetectInfo import loadFTPDetectInfo
from Math import jd2Date


tmpdir = os.getenv('TEMP', default='/tmp')
isodate_format_entry = "%Y-%m-%dT%H:%M:%S.%f"
isodate_format_file = "%Y-%m-%dT%H:%M:%S"


def createECSV(ftpFile, required_event):
    """ Save the picks into the GDEF ECSV standard. 
    Arguments: 
        ftpFile:        string  full path and ftp File name
        required_event  string  target event in the format isodate_format_entry (see below)
    """
    out_str=''

    outdir, _ = os.path.split(ftpFile)
    ppfilename = os.path.join(outdir, 'platepars_all_recalibrated.json')
    if not os.path.isfile(ppfilename):
        return 'no platepar file - cannot continue'

    with open(ppfilename) as f:
        try:
            platepars_recalibrated_dict = json.load(f)
        except:
            return 'malformed platepar file - cannot continue'
    kvals = platepars_recalibrated_dict[list(platepars_recalibrated_dict.keys())[0]]
    meteors = loadFTPDetectInfo(ftpFile, locdata=kvals)

    revt = required_event.replace('-','').replace(':','').replace('T','_').replace('.','_')
    met = None
    for thismet in meteors:
        if revt in thismet.ff_name:
            met = thismet
            break
    if not met:
        return 'no match in the ftpdetect file, check time'
    print(f'matched {met.ff_name}')
    dt_ref = jd2Date(met.jdt_ref, dt_obj=True)
    # meteors split over 2 ffs get merged into one entry relative to the 1st frame, indexed by both ff names
    ffnames = os.path.basename(met.ff_name).split(',')
    ffname = ffnames[0]
    try:
        print(f'trying to find plate for {ffname}')
        platepar = platepars_recalibrated_dict[ffname]
    except Exception:
        return 'no match in the platepar file'

    ffdate = datetime.datetime.strptime(ffname[10:29], '%Y%m%d_%H%M%S_%f')
    obscalib = ffdate + datetime.timedelta(microseconds=(met.time_data[0]*1e6))
   
    # Write the meta header
    meta_dict = {
        'obs_latitude': platepar['lat'],   # Decimal signed latitude (-90 S to +90 N)
        'obs_longitude': platepar['lon'],  # Decimal signed longitude (-180 W to +180 E)
        'obs_elevation': platepar['elev'], # Altitude in metres above MSL. Note not WGS84
        'origin': 'ukmda',              # The software which produced the data file
        'camera_id': met.station_id,    # The code name of the camera, likely to be network-specific
        'cx': platepar['X_res'],           # Horizontal camera resolution in pixels
        'cy': platepar['Y_res'],           # Vertical camera resolution in pixels
        'photometric_band': 'unknown',  # The photometric band of the star catalogue
        'image_file': ffnames,           # The name of the original image or video
        'isodate_start_obs': str(dt_ref.strftime(isodate_format_entry)),               # The date and time of the start of the video or exposure
        'isodate_calib': str(obscalib.strftime(isodate_format_entry)),          # The date and time corresponding to the astrometric calibration
        'astrometry_number_stars': len(platepar['star_list']),       # The number of stars identified and used in the astrometric calibration
        'mag_label': 'mag',                         # The label of the Magnitude column in the Point Observation data
        'no_frags': 1,                              # The number of meteoroid fragments described in this data
        'obs_az': platepar['az_centre'],            # The azimuth of the centre of the field of view in decimal degrees. North = 0, increasing to the East
        'obs_ev': platepar['alt_centre'],           # The elevation of the centre of the field of view in decimal degrees. Horizon =0, Zenith = 90
        'obs_rot': platepar['rotation_from_horiz'], # Rotation of the field of view from horizontal, decimal degrees. Clockwise is positive
        'fov_horiz': platepar['fov_h'],             # Horizontal extent of the field of view, decimal degrees
        'fov_vert': platepar['fov_v'],              # Vertical extent of the field of view, decimal degrees
    }


    # Write the header
    out_str += """# %ECSV 0.9
# ---
# datatype:
# - {name: datetime, datatype: string}
# - {name: ra, unit: deg, datatype: float64}
# - {name: dec, unit: deg, datatype: float64}
# - {name: azimuth, datatype: float64}
# - {name: altitude, datatype: float64}
# - {name: mag_data, datatype: float64}
# - {name: x_image, unit: pix, datatype: float64}
# - {name: y_image, unit: pix, datatype: float64}
# delimiter: ','
# meta: !!omap
"""
    # Add the meta information
    for key in meta_dict:

        value = meta_dict[key]

        if isinstance(value, str):
            value_str = "'{:s}'".format(value)
        else:
            value_str = str(value)

        out_str += "# - {" + "{:s}: {:s}".format(key, value_str) + "}\n"


    out_str += "# schema: astropy-2.0\n"
    out_str += "datetime,ra,dec,azimuth,altitude,mag_data,x_image,y_image\n"


    # Add the data
    for f, t, ra, dec, azim, alt, x, y, mag in zip(met.frames,met.time_data, met.ra_data, 
            met.dec_data, met.azim_data, met.elev_data, met.x_data, met.y_data, met.mag_data):

        musadj = t*1e6
        ptdate = ffdate + datetime.timedelta(microseconds=musadj)
        ra = np.degrees(ra)
        dec = np.degrees(dec)
        azim = np.degrees(azim)
        alt = np.degrees(alt)
        entry = [ptdate.strftime(isodate_format_entry), "{:10.6f}".format(ra),
            "{:+10.6f}".format(dec), "{:10.6f}".format(azim), "{:+10.6f}".format(alt),
            "{:+7.2f}".format(mag), "{:9.3f}".format(x), "{:9.3f}".format(y)]

        out_str += ",".join(entry) + "\n"

    return out_str


def fetchECSV(camid, reqevent):
    s3bucket = os.getenv('ARCHBUCKET', default='ukmda-shared')
    s3 = boto3.resource('s3')

    # construct the path
    if '-' in reqevent:
        try:
            dt = datetime.datetime.strptime(reqevent, isodate_format_entry)
        except Exception:
            try:
                dt = datetime.datetime.strptime(reqevent, isodate_format_file)
            except Exception:
                return 'check date format'
    else:
        try:
            dt = datetime.datetime.strptime(reqevent, '%Y%m%d_%H%M%S_%f')
        except Exception:
            try:
                dt = datetime.datetime.strptime(reqevent, '%Y%m%d_%H%M%S')
            except Exception:
                return 'check date format'
    if dt.hour < 12:
        dt = dt + datetime.timedelta(days=-1)
    ymd = dt.strftime('%Y%m%d')
    pref = f'matches/RMSCorrelate/{camid}/{camid}_{ymd}'

    localftpname = None
    ppname = None
    cfgname = None
    for _, obj in enumerate(s3.Bucket(s3bucket).objects.filter(Prefix=pref)):
        fldr = obj.key.split('/')[3].strip()
        localf = os.path.basename(obj.key)
        if f'FTPdetectinfo_{fldr}.txt' in obj.key:
            localftpname = os.path.join(tmpdir, localf)
            s3.meta.client.download_file(s3bucket, obj.key, localftpname)
        elif 'platepars_all_recalibrated.json' in obj.key:
            ppname = os.path.join(tmpdir, localf)
            s3.meta.client.download_file(s3bucket, obj.key, ppname)

    if localftpname is None:
        # download the camera details file and find the location
        ddb = boto3.resource('dynamodb', region_name='eu-west-2') 
        loc = findSite(camid, ddb)
        if loc is False:
            return 'site not found'
        ym = f'{dt.year}{dt.month:02d}'
        ymd = f'{dt.year}{dt.month:02d}{dt.day:02d}'   
        s3path = f'archive/{loc}/{camid}/{dt.year}/{ym}/{ymd}/'

        print(f'no objects found at {pref}, trying alternate location {s3path}')
        # get the config, platepar and ftpfile
        localftpname = None
        ppname = None
        bucket = s3.Bucket(s3bucket)
        for obj in bucket.objects.filter(Prefix = s3path):
            localf = os.path.basename(obj.key)
            if localf == 'platepars_all_recalibrated.json':
                ppname = os.path.join(tmpdir, localf)
                s3.meta.client.download_file(s3bucket, obj.key, ppname)
            elif 'FTPdetect' in localf and 'uncal' not in localf and 'backup' not in localf:
                localftpname = os.path.join(tmpdir, localf)
                s3.meta.client.download_file(s3bucket, obj.key, localftpname)
    
    # if we got the ftpfile, call createECSV
    if localftpname is not None:
        ecsvstr = createECSV(localftpname, reqevent)
        removefiles(localftpname, ppname, cfgname)
        return ecsvstr
        
    removefiles(localftpname, ppname, cfgname)
    return 'not available, check details'


def findSite(stationid, ddb=None):
    table = ddb.Table('camdetails')
    res = table.query(KeyConditionExpression=Key('stationid').eq(stationid))
    if res['Count'] > 0:
        return res['Items'][0]['site']
    else:
        return False


def removefiles(localftpname, ppname, cfgname):
    try:
        os.remove(localftpname)
    except:
        pass
    try:
        os.remove(ppname)
    except:
        pass
    try:
        os.remove(cfgname)
    except:
        pass


def lambda_handler(event, context):
    qs = event['queryStringParameters']
    if qs is not None:
        if 'stat' in qs or 'dt' in qs:
            stat = qs['stat']
            dt = qs['dt']
            #print(stat, dt)
            ecsvstr = fetchECSV(stat, dt)
            return {
                'statusCode': 200,
                'body': ecsvstr # json.dumps(res)
            }
    else:
        return {
            'statusCode': 200,
            'body': "usage: getecsv?stat=UKxxxx&dt=YYYY-mm-ddTHH:MM:SS.fff"
        }


if __name__ == '__main__':
    camid = sys.argv[1]
    reqdate = sys.argv[2]
    ecsvstr = fetchECSV(camid, reqdate)
    #ecsvstr = fetchECSV('UK001M', '2022-01-10T19:43:30.567111')
    print(ecsvstr)
