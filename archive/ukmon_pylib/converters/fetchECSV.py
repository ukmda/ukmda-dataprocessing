#
# Function to save an FTPdetect file and platepar as ECSV files
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import sys
import json
import datetime
import numpy as np
import boto3

from meteortools.fileformats import loadFTPDetectInfo
from meteortools.utils import jd2Date


tmpdir = os.getenv('TEMP', default='/tmp')
isodate_format_entry = "%Y-%m-%dT%H:%M:%S.%f"
isodate_format_file = "%Y-%m-%dT%H:%M:%S"


def createECSV(ftpFile, required_event = None):
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

    #print(f'{len(meteors)} in file')

    if required_event is not None:
        fmtstr = isodate_format_entry[:min(len(required_event)-2, 24)]
        reqdate = datetime.datetime.strptime(required_event, fmtstr)
        statid = ftpFile.split('_')[1]
        reqstr = f'FF_{statid}_{reqdate.strftime("%Y%m%d_%H%M%S")}'
        reqevt = reqdate.timestamp()
        # check input precision
        spls = required_event.split('.')
        if len(spls) == 1:
            prec = 11
        else:
            decis = spls[1]
            prec = pow(10, -len(decis))
    else:
        reqevt = 0
        prec = 11
        reqstr = 'FF'

    for met in meteors:
        # Reference time
        dt_ref = jd2Date(met.jdt_ref, dt_obj=True)
        
        ffname = os.path.basename(met.ff_name)
        try:
            platepar = platepars_recalibrated_dict[ffname]
        except Exception:
            continue
        evtdate = datetime.datetime.strptime(ffname[10:29], '%Y%m%d_%H%M%S_%f')
        obscalib = evtdate + datetime.timedelta(microseconds=(met.time_data[0]*1e6))
        
        if reqevt > 0 and prec != 11 and abs(obscalib.timestamp() - reqevt) >= prec:
            continue
        if prec == 11 and reqstr not in ffname:
            continue

        #print('found match')
        azim, elev = platepar['az_centre'], platepar['alt_centre']
        fov_horiz, fov_vert = platepar['fov_h'], platepar['fov_v']

        # Write the meta header
        meta_dict = {
            'obs_latitude': platepar['lat'],   # Decimal signed latitude (-90 S to +90 N)
            'obs_longitude': platepar['lon'],  # Decimal signed longitude (-180 W to +180 E)
            'obs_elevation': platepar['elev'], # Altitude in metres above MSL. Note not WGS84
            'origin': 'ukmon',              # The software which produced the data file
            'camera_id': met.station_id,    # The code name of the camera, likely to be network-specific
            'cx': platepar['X_res'],           # Horizontal camera resolution in pixels
            'cy': platepar['Y_res'],           # Vertical camera resolution in pixels
            'photometric_band': 'unknown',  # The photometric band of the star catalogue
            'image_file': ffname,           # The name of the original image or video
            'isodate_start_obs': str(dt_ref.strftime(isodate_format_entry)),               # The date and time of the start of the video or exposure
            'isodate_calib': str(obscalib.strftime(isodate_format_entry)),          # The date and time corresponding to the astrometric calibration
            'astrometry_number_stars': len(platepar['star_list']),       # The number of stars identified and used in the astrometric calibration
            'mag_label': 'mag',             # The label of the Magnitude column in the Point Observation data
            'no_frags': 1,                  # The number of meteoroid fragments described in this data
            'obs_az': azim,                 # The azimuth of the centre of the field of view in decimal degrees. North = 0, increasing to the East
            'obs_ev': elev,                 # The elevation of the centre of the field of view in decimal degrees. Horizon =0, Zenith = 90
            'obs_rot': platepar['rotation_from_horiz'],                  # Rotation of the field of view from horizontal, decimal degrees. Clockwise is positive
            'fov_horiz': fov_horiz,         # Horizontal extent of the field of view, decimal degrees
            'fov_vert': fov_vert,           # Vertical extent of the field of view, decimal degrees
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
            ptdate = evtdate + datetime.timedelta(microseconds=musadj)
            #print(evtdate, t, musadj)
            #if meta_dict['isodate_calib'] is None:
            #    meta_dict['isodate_calib'] = str(ptdate.strftime(isodate_format_file))
            #print(meta_dict['isodate_calib'], ptdate)
            # Add an entry to the ECSV file
            ra = np.degrees(ra)
            dec = np.degrees(dec)
            azim = np.degrees(azim)
            alt = np.degrees(alt)
            entry = [ptdate.strftime(isodate_format_entry), "{:10.6f}".format(ra),
                "{:+10.6f}".format(dec), "{:10.6f}".format(azim), "{:+10.6f}".format(alt),
                "{:+7.2f}".format(mag), "{:9.3f}".format(x), "{:9.3f}".format(y)]

            out_str += ",".join(entry) + "\n"

        # ESCV files name
        #ecsv_file_name = obscalib.strftime(isodate_format_file) + '_RMS_' + met.station_id + ".ecsv"

        #ecsv_file_path = os.path.join(outdir, ecsv_file_name)

        # Write file to disk
        #with open(ecsv_file_path, 'w') as f:
        #    f.write(out_str)

    if len(out_str) == 0:
        out_str = 'issue getting data, check details'
    return out_str


def ftpToECSV(ftpFile, outdir=None):
    if outdir is None:
        outdir, _ = os.path.split(ftpFile)
    ecsvstr = createECSV(ftpFile)
    ecsvs = ecsvstr.split('# %ECSV')
    for ecsv in ecsvs:
        if len(ecsv) < 10:
            continue
        data = '# %ECSV' + ecsv
        evtdt = data.split('isodate_calib:')[1][0:29].strip().replace("'",'')
        statid = data.split('camera_id:')[1][0:10].strip().replace("'",'').replace('}','')
        evtdt = evtdt.replace('-','').replace('T','_').replace(':','').replace('.','_')
        fname = os.path.join(outdir, f'FF_{statid}_{evtdt}_UKMON.ecsv')
        with open(fname,'w') as outf:
            outf.write(data)
        print("ESCV file saved to:", fname)
    return 


def fetchECSV(camid, reqevent):
    s3bucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    s3 = boto3.resource('s3')

    # construct the path
    try:
        dt = datetime.datetime.strptime(reqevent, isodate_format_entry)
    except:
        dt = datetime.datetime.strptime(reqevent, isodate_format_file)

    if dt.hour < 12:
        dt = dt + datetime.timedelta(days=-1)
    ymd = dt.strftime('%Y%m%d')
    pref = f'matches/RMSCorrelate/{camid}/{camid}_{ymd}'
    #print(f'looking for {pref}')

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
        s3object = 'consolidated/camera-details.csv'
        camfname = os.path.join(tmpdir, 'camera-details.csv')
        s3.meta.client.download_file(s3bucket, s3object, camfname)
        loc=''
        with open(camfname) as inf:
            lis = inf.readlines()
            for li in lis:
                if camid in li:
                    loc = li.split(',')[0]
                    trucam = li.split(',')[1]
                    break
        os.remove(camfname)
        if loc == '':
            print('camera not found')
            return    
        ym = f'{dt.year}{dt.month:02d}'
        ymd = f'{dt.year}{dt.month:02d}{dt.day:02d}'   
        s3path = f'archive/{loc}/{trucam}/{dt.year}/{ym}/{ymd}/'

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
        print(f'using {localftpname} and {ppname}')
        ecsvstr = createECSV(localftpname, reqevent)
        if len(ecsvstr) != 0:
            removefiles(localftpname, ppname, cfgname)
        return ecsvstr
        
    removefiles(localftpname, ppname, cfgname)
    return 'not available, check details'


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
    stat = qs['stat']
    dt = qs['dt']
    #print(stat, dt)
    ecsvstr = fetchECSV(stat, dt)
    return {
        'statusCode': 200,
        'body': ecsvstr # json.dumps(res)
    }


if __name__ == '__main__':
    camid = sys.argv[1]
    reqdate = sys.argv[2]
    ecsvstr = fetchECSV(camid, reqdate)
    #ecsvstr = fetchECSV('UK001M', '2022-01-10T19:43:30.567111')
    print(ecsvstr)
