#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
import datetime
import pytz
import json
import time
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np

from supportFuncs import datetime2JD, altAz2RADec, polarToCartesian, cartesianToPolar
from supportFuncs import angularSeparation, greatCircle, fitGreatCircle, greatCirclePhase
from supportFuncs import filenameToDatetime, readFTPdetectinfo, loadConfigFromDirectory

from ShowerAssociation import showerAssociation


class PlateparDummy:
    def __init__(self, **entries):
        """ This class takes a platepar dictionary and converts it into an object. """

        self.__dict__.update(entries)
        if not hasattr(self, 'UT_corr'):
            self.UT_corr = 0


def writeUkmonCsv(dir_path, file_name, data):
    """ Write the a Ukmon specific CSV file for single-station data. 

    Arguments:
        dir_path: [str] Directory where the file will be written to.
        file_name: [str] Name of the UFOOrbit CSV file.
        data: [list] A list of meteor entries.

    """
    with open(os.path.join(dir_path, file_name), 'w') as f:

        # Write the header - no
        #f.write("Ver,Y,M,D,h,m,s,Mag,Dur,Az1,Alt1,Az2,Alt2,Ra1,Dec1,Ra2,Dec2,ID,Long,Lat,Alt,Tz,AngVel,Shwr,Filename,Dtstamp\n")

        # Write meteor data to file
        for line in data:

            dt, peak_mag, duration, azim1, alt1, azim2, alt2, ra1, dec1, ra2, dec2, cam_code, lon, lat, \
                elev, UT_corr, shwr, fname, angvel = line

            # Convert azimuths to the astronomical system (+W of due S)
            azim1 = (azim1 - 180) % 360
            azim2 = (azim2 - 180) % 360

            # cater for the possibility that secs+microsecs > 59.99 and would round up to 60
            # causing an invalid time to be written eg 20,55,60.00, instead of 20,56,0.00
            secs = round(dt.second + dt.microsecond / 1000000, 2)
            if secs > 59.99: 
                tmpdt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0, 0, 
                    tzinfo=pytz.UTC) 
                # add 60 seconds on to the datetime
                dt = tmpdt + datetime.timedelta(seconds = secs)
            dtstamp = dt.timestamp()

            f.write('{:s},{:4d},{:2d},{:2d},{:2d},{:2d},{:4.2f},{:.2f},{:.3f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:s},{:.6f},{:.6f},{:.1f},{:.1f},{:7f},{:s},{:s},{:.6f}\n'.format(
                'UM1', dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond/1000000, 
                peak_mag, duration, azim1, alt1, azim2, alt2, ra1, dec1, ra2, dec2, cam_code, lon, lat, 
                elev, UT_corr, angvel, shwr, fname, dtstamp))

    s3 = boto3.resource('s3')
    s3bucket = os.getenv('ARCHBUCKET', default='ukmon-shared')
    outdir = os.getenv('OUTDIR', default='matches/single/new')
    outn = outdir + '/' + file_name
    fullname = os.path.join(dir_path, file_name)
    s3.meta.client.upload_file(fullname, s3bucket, outn, ExtraArgs={'ContentType': 'text/csv'})


def FTPdetectinfo2UkmonCsv(dir_path):
    """ Convert the FTPdetectinfo file into a ukmon specific CSV file. 
        
    Arguments:
        dir_path: [str] Path of the directory which contains the FTPdetectinfo file.
        out_path: [str] Path of the directory to save the results into

    """
    # Load the FTPdetectinfo file

    ftpdetectinfo_name = None
    for name in os.listdir(dir_path):
        # Find FTPdetectinfo
        if name.startswith("FTPdetectinfo") and name.endswith('.txt') and \
                ("backup" not in name) and ("uncalibrated" not in name):
            ftpdetectinfo_name = name
            break
    if ftpdetectinfo_name is None:
        print(f'Ignoring {dir_path} as no ftpdetect file')
        return 

    ppfilename = os.path.join(dir_path, 'platepars_all_recalibrated.json')
    if not os.path.isfile(ppfilename):
        print(f'Skipping {ftpdetectinfo_name} as no platepar file')
        return 

    with open(ppfilename) as f:
        try:
            platepars_recalibrated_dict = json.load(f)
        except:
            print(f'Skipping {ftpdetectinfo_name} as malformed platepar file')
            return 


    # Load the FTPdetectinfo file
    try:
        meteor_list = readFTPdetectinfo(dir_path, ftpdetectinfo_name)
    except Exception:
        print(f'Malformed FTPdetect file {ftpdetectinfo_name}') 
        return 
    if len(meteor_list) == 0:
        print(f'Ignoring {ftpdetectinfo_name} as no meteors')
        return
    
    # load the config file then overwrite the bits of importance
    config = loadConfigFromDirectory(dir_path, '.config')

    fflst = list(platepars_recalibrated_dict.keys())
    if len(fflst) > 0: 
        ff1 = fflst[0]
        pp1 = platepars_recalibrated_dict[ff1]
        config.latitude = pp1['lat']
        config.longitude = pp1['lon']
        config.elevation = pp1['elev']
        # get the shower associations
        shwrs = showerAssociation(config, os.path.join(dir_path,ftpdetectinfo_name))
    else:
        print(f'Ignoring {ftpdetectinfo_name} as platepar file empty')
        return 
    # Init the UFO format list
    ufo_meteor_list = []

    # Go through every meteor in the list
    for meteor in meteor_list:

        ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi, \
            meteor_meas = meteor

        # Load the platepar from the platepar dictionary
        if ff_name in platepars_recalibrated_dict:
            pp_dict = platepars_recalibrated_dict[ff_name]
            pp = PlateparDummy(**pp_dict)

        else:
            print('Skipping {:s} because no platepar was found for this FF file!'.format(ff_name))
            continue
        
        # Convert the FF file name into time
        dt = filenameToDatetime(ff_name)
        try: 
            shwrdets = shwrs[(ff_name,meteor_No)]
            if shwrdets[1] is not None:
                shwr = shwrdets[1].name
            else:
                shwr='spo'
        except KeyError:
            shwr='spo'

        # Extract measurements
        calib_status, frame_n, x, y, ra, dec, azim, elev, inten, mag = np.array(meteor_meas).T

        # If the meteor wasn't calibrated, skip it
        if not np.all(calib_status):
            print('Meteor {:d} was not calibrated, skipping it...'.format(meteor_No))
            continue

        # Compute the peak magnitude
        peak_mag = np.min(mag)

        # Compute the total duration
        first_frame = np.min(frame_n)
        last_frame = np.max(frame_n) 
        duration = (last_frame - first_frame)/fps


        # Compute times of first and last points
        dt1 = dt + datetime.timedelta(seconds=first_frame/fps)
        dt2 = dt + datetime.timedelta(seconds=last_frame/fps)

        
        # Fit a great circle to Az/Alt measurements and compute model beg/end RA and Dec ###

        # Convert the measurement Az/Alt to cartesian coordinates
        # NOTE: All values that are used for Great Circle computation are:
        #   theta - the zenith angle (90 deg - altitude)
        #   phi - azimuth +N of due E, which is (90 deg - azim)
        x, y, z = polarToCartesian(np.radians((90 - azim) % 360), np.radians(90 - elev))

        # Fit a great circle
        C, theta0, phi0 = fitGreatCircle(x, y, z)

        # Get the first point on the great circle
        phase1 = greatCirclePhase(np.radians(90 - elev[0]), np.radians((90 - azim[0]) % 360), 
            theta0, phi0)
        alt1, azim1 = cartesianToPolar(*greatCircle(phase1, theta0, phi0))
        alt1 = 90 - np.degrees(alt1)
        azim1 = (90 - np.degrees(azim1)) % 360

        # Get the last point on the great circle
        phase2 = greatCirclePhase(np.radians(90 - elev[-1]), np.radians((90 - azim[-1]) % 360),
            theta0, phi0)
        alt2, azim2 = cartesianToPolar(*greatCircle(phase2, theta0, phi0))
        alt2 = 90 - np.degrees(alt2)
        azim2 = (90 - np.degrees(azim2)) % 360

        # Compute RA/Dec from Alt/Az
        ra1, dec1 = altAz2RADec(azim1, alt1, datetime2JD(dt1), pp.lat, pp.lon)
        ra2, dec2 = altAz2RADec(azim2, alt2, datetime2JD(dt2), pp.lat, pp.lon)

        angLength = angularSeparation(np.radians(ra1), np.radians(dec1), np.radians(ra2), np.radians(dec2))
        angVel = np.degrees(angLength)/duration

        ufo_meteor_list.append([dt1, peak_mag, duration, azim1[0], alt1[0], azim2[0], alt2[0], 
            ra1, dec1, ra2, dec2, cam_code, pp.lon, pp.lat, pp.elev, pp.UT_corr, 
            shwr, ff_name, angVel])


    # Construct a file name for the UFO file, which is the FTPdetectinfo file without the FTPdetectinfo 
    #   part
    ufo_file_name = ftpdetectinfo_name.replace('FTPdetectinfo_', 'ukmon_').replace('.txt', '') + '.csv'

    # Write the ukmon-specific output file
    writeUkmonCsv(dir_path, ufo_file_name, ufo_meteor_list)


def addRowCamTimings(s3bucket, s3object):
    s3c = boto3.client('s3')
    dtstamp = s3c.head_object(Bucket=s3bucket, Key=s3object)['LastModified']
    ddb = boto3.resource('dynamodb', region_name='eu-west-1') 
    table = ddb.Table('ukmon_uploadtimes')
    # s3object = matches/RMSCorrelate/UK0006/UK0006_20221121_164424_325844/FTPdetectinfo_UK0006_20221121_164424_325844.txt
    spls = s3object.split('/')
    camid = spls[2]
    ftpname = spls[-1]
    ftpspls = ftpname.split('_')
    rundate = ftpspls[2] + '_' + ftpspls[3]
    manual = False
    uploaddate = dtstamp.strftime('%Y%m%d')
    uploadtime = dtstamp.strftime('%H%M%S')
    table.put_item(
        Item={
            'stationid': camid,
            'dtstamp': uploaddate + '_' + uploadtime,
            'uploaddate': int(uploaddate),
            'uploadtime': int(uploadtime),
            'manual': manual,
            'rundate': rundate
        }
    )   
    return 


def ftpToUkmon(s3bucket, s3object):
    s3 = boto3.resource('s3')

    if 'FTPdetectinfo' not in s3object or 'backup' in s3object or 'detected' in s3object \
            or 'uncalibrated' in s3object: 
        # its not a calibrated FTPdetect file so ignore it
        print(f'not a relevant file {s3object}')
        return 0
    
    tmpdir = mkdtemp()
    pth, fn = os.path.split(s3object)
    s3.meta.client.download_file(s3bucket, s3object, os.path.join(tmpdir, fn))

    # check if it contains calibrated meteors; if not, skip further downloads
    recal = False
    with open(os.path.join(tmpdir, fn), 'r') as inf:
        lis = inf.readlines()
    if len(lis) == 0:
        print(f'missing content in FTP file {pth}')
        return 0
    metcount = int(lis[0].strip().split()[3])

    # check data recalibrated 
    for li in lis:
        if 'Recalibrated' in li:
            recal = True
            break
    
    if metcount == 0 or recal is False:
        print(f'Meteorcount 0 or data uncalibrated in {pth}')
        rmtree(tmpdir)
        return 

    s3c = boto3.client('s3')
    ppn = os.path.join(pth, 'platepars_all_recalibrated.json')
    for i in range(11):
        try:
            response = s3c.head_object(Bucket=s3bucket, Key=ppn)
            if response['ContentLength'] > 100: 
                outn = os.path.join(tmpdir, 'platepars_all_recalibrated.json')
                s3.meta.client.download_file(s3bucket, ppn, outn)
            break
        except:
            time.sleep(1)
    if i == 10:
        print(f'platepars_all is missing for {pth}')
        return 
    cfg = os.path.join(pth, '.config')
    for i in range(11):
        try:
            response = s3c.head_object(Bucket=s3bucket, Key=cfg)
            if response['ContentLength'] > 100: 
                outn = os.path.join(tmpdir, '.config')
                s3.meta.client.download_file(s3bucket, cfg, outn)
            break
        except:
            time.sleep(1)
    if i == 10:
        print(f'.config file is missing for {pth}')
        return 

    #print('got files')

    FTPdetectinfo2UkmonCsv(tmpdir)

    rmtree(tmpdir)
    return 0


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    ftpToUkmon(s3bucket, s3object)
    addRowCamTimings(s3bucket, s3object)

    return 0
