#
# Load an FTPdetectInfo file - copied from RMS and amended to remove dependencies
#

import sys
import os
import numpy as np
import configparser as crp

from MeteorObservation import MeteorObservation
from Math import angleBetweenSphericalCoords, date2JD


def loadFTPDetectInfo(ftpdetectinfo_file_name, time_offsets=None,
        join_broken_meteors=True):
    """

    Arguments:
        ftpdetectinfo_file_name: [str] Path to the FTPdetectinfo file.
        stations: [dict] A dictionary where the keys are stations IDs, and values are lists of:
            - latitude +N in radians
            - longitude +E in radians
            - height in meters
        

    Keyword arguments:
        time_offsets: [dict] (key, value) pairs of (stations_id, time_offset) for every station. None by 
            default.
        join_broken_meteors: [bool] Join meteors broken across 2 FF files.


    Return:
        meteor_list: [list] A list of MeteorObservation objects filled with data from the FTPdetectinfo file.

    """
    dirname, fname = os.path.split(ftpdetectinfo_file_name)
    cfgfile = os.path.join(dirname, '.config')    
    cfg = crp.ConfigParser()
    cfg.read(cfgfile)
    lat = float(cfg['System']['latitude'].split()[0])
    lon = float(cfg['System']['longitude'].split()[0])
    height = float(cfg['System']['elevation'].split()[0])
    statid= fname.split('_')[1]
    stations={}
    stations[statid] = [np.radians(lat), np.radians(lon), height*1000]

    meteor_list = []

    with open(ftpdetectinfo_file_name) as f:
        # Skip the header
        for i in range(11):
            next(f)

        current_meteor = None

        bin_name = False
        cal_name = False
        meteor_header = False

        for line in f:
            # Skip comments
            if line.startswith("#"):
                continue

            line = line.replace('\n', '').replace('\r', '')

            # Skip the line if it is empty
            if not line:
                continue

            if '-----' in line:
                # Mark that the next line is the bin name
                bin_name = True

                # If the separator is read in, save the current meteor
                if current_meteor is not None:
                    current_meteor.finish()
                    meteor_list.append(current_meteor)
                continue

            if bin_name:
                bin_name = False

                # Mark that the next line is the calibration file name
                cal_name = True

                # Save the name of the FF file
                ff_name = line

                # Extract the reference time from the FF bin file name
                line = line.split('_')

                # Count the number of string segments, and determine if it the old or new CAMS format
                if len(line) == 6:
                    sc = 1
                else:
                    sc = 0

                ff_date = line[1 + sc]
                ff_time = line[2 + sc]
                milliseconds = line[3 + sc]

                year = ff_date[:4]
                month = ff_date[4:6]
                day = ff_date[6:8]

                hour = ff_time[:2]
                minute = ff_time[2:4]
                seconds = ff_time[4:6]

                year, month, day, hour, minute, seconds, milliseconds = map(int, [year, month, day, hour, 
                    minute, seconds, milliseconds])

                # Calculate the reference JD time
                jdt_ref = date2JD(year, month, day, hour, minute, seconds, milliseconds)
                continue

            if cal_name:
                cal_name = False
                # Mark that the next line is the meteor header
                meteor_header = True
                continue

            if meteor_header:
                meteor_header = False
                line = line.split()

                # Get the station ID and the FPS from the meteor header
                station_id = line[0].strip()
                fps = float(line[3])

                # Try converting station ID to integer
                try:
                    station_id = int(station_id)
                except:
                    pass

                # If the time offsets were given, apply the correction to the JD
                if time_offsets is not None:
                    if station_id in time_offsets:
                        print('Applying time offset for station {:s} of {:.2f} s'.format(str(station_id),
                            time_offsets[station_id]))

                        jdt_ref += time_offsets[station_id]/86400.0
                    else:
                        print('Time offset for given station not found!')

                # Get the station data
                if station_id in stations:
                    lat, lon, height = stations[station_id]
                else:
                    print('ERROR! No info for station ', station_id, ' found in CameraSites.txt file!')
                    print('Exiting...')
                    break
                # Init a new meteor observation
                current_meteor = MeteorObservation(jdt_ref, station_id, lat, lon, height, fps,
                    ff_name=ff_name)
                continue

            # Read in the meteor observation point
            if (current_meteor is not None) and (not bin_name) and (not cal_name) and (not meteor_header):

                line = line.replace('\n', '').split()

                # Read in the meteor frame, RA and Dec
                frame_n = float(line[0])
                x = float(line[1])
                y = float(line[2])
                ra = float(line[3])
                dec = float(line[4])
                azim = float(line[5])
                elev = float(line[6])

                # Read the visual magnitude, if present
                if len(line) > 8:
                    mag = line[8]
                    if mag == 'inf':
                        mag = None
                    else:
                        mag = float(mag)
                else:
                    mag = None

                # Add the measurement point to the current meteor 
                current_meteor.addPoint(frame_n, x, y, azim, elev, ra, dec, mag)

        # Add the last meteor the the meteor list
        if current_meteor is not None:
            current_meteor.finish()
            meteor_list.append(current_meteor)

    # Concatenate observations across different FF files ###
    if join_broken_meteors:

        # Go through all meteors and compare the next observation
        merged_indices = []
        for i in range(len(meteor_list)):

            # If the next observation was merged, skip it
            if (i + 1) in merged_indices:
                continue

            # Get the current meteor observation
            met1 = meteor_list[i]

            if i >= (len(meteor_list) - 1):
                break

            # Get the next meteor observation
            met2 = meteor_list[i + 1]
            
            # Compare only same station observations
            if met1.station_id != met2.station_id:
                continue

            # Extract frame number
            met1_frame_no = int(met1.ff_name.split("_")[-1].split('.')[0])
            met2_frame_no = int(met2.ff_name.split("_")[-1].split('.')[0])

            # Skip if the next FF is not exactly 256 frames later
            if met2_frame_no != (met1_frame_no + 256):
                continue


            # Check for frame continouty
            if (met1.frames[-1] < 254) or (met2.frames[0] > 2):
                continue

            # Check if the next frame is close to the predicted position 

            # Compute angular distance between the last 2 points on the first FF
            ang_dist = angleBetweenSphericalCoords(met1.dec_data[-2], met1.ra_data[-2], met1.dec_data[-1],
                met1.ra_data[-1])

            # Compute frame difference between the last frame on the 1st FF and the first frame on the 2nd FF
            df = met2.frames[0] + (256 - met1.frames[-1])

            # Skip the pair if the angular distance between the last and first frames is 2x larger than the 
            #   frame difference times the expected separation
            ang_dist_between = angleBetweenSphericalCoords(met1.dec_data[-1], met1.ra_data[-1],
                met2.dec_data[0], met2.ra_data[0])

            if ang_dist_between > 2*df*ang_dist:
                continue

            # If all checks have passed, merge observations ###
            # Recompute the frames
            frames = 256.0 + met2.frames

            # Recompute the time data
            time_data = frames/met1.fps

            # Add the observations to first meteor object
            met1.frames = np.append(met1.frames, frames)
            met1.time_data = np.append(met1.time_data, time_data)
            met1.x_data = np.append(met1.x_data, met2.x_data)
            met1.y_data = np.append(met1.y_data, met2.y_data)
            met1.azim_data = np.append(met1.azim_data, met2.azim_data)
            met1.elev_data = np.append(met1.elev_data, met2.elev_data)
            met1.ra_data = np.append(met1.ra_data, met2.ra_data)
            met1.dec_data = np.append(met1.dec_data, met2.dec_data)
            met1.mag_data = np.append(met1.mag_data, met2.mag_data)

            # Merge the FF file name and create a list
            if (met1.ff_name is not None) and (met2.ff_name is not None):
                met1.ff_name = met1.ff_name + ',' + met2.ff_name

            # Sort all observations by time
            met1.finish()

            # Indicate that the next observation is to be skipped
            merged_indices.append(i + 1)

        # Removed merged meteors from the list
        meteor_list = [element for i, element in enumerate(meteor_list) if i not in merged_indices]

    return meteor_list


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('usage: python ftpDetectInfo.py ftpfile')
        print('note: requires .config and platepar to be in the same folder')
        exit(0)
        
    ftpname = sys.argv[1]
    metlist = loadFTPDetectInfo(sys.argv[1])
    m1 = metlist[0]
    print(m1.jdt_ref, m1.ff_name)
    for f,t,r,d,a,e,x,y,m in zip(m1.frames,m1.time_data, m1.ra_data, m1.dec_data, m1.azim_data, m1.elev_data, m1.x_data, m1.y_data, m1.mag_data):
        print(f,t,r,d,a,e,x,y,m)
