#
# Function to save an FTPdetect file and platepar as ECSV files
#
import os
import sys
import json
import datetime
import numpy as np

from fileformats.ftpDetectInfo import loadFTPDetectInfo
from wmpl.Utils.TrajConversions import jd2Date


def saveECSV(ftpFile):
    """ Save the picks into the GDEF ECSV standard. """
    isodate_format_file = "%Y-%m-%dT%H_%M_%S"
    isodate_format_entry = "%Y-%m-%dT%H:%M:%S.%f"

    meteors = loadFTPDetectInfo(ftpFile)
    outdir, _ = os.path.split(ftpFile)
    ppfilename = os.path.join(outdir, 'platepars_all_recalibrated.json')
    if not os.path.isfile(ppfilename):
        print('no platepar file - cannot continue')
        return 

    with open(ppfilename) as f:
        try:
            platepars_recalibrated_dict = json.load(f)
        except:
            print('malformed platepar file - cannot continue')
            return 

    for met in meteors:
        # Reference time
        dt_ref = jd2Date(met.jdt_ref, dt_obj=True)
        
        # ESCV files name
        ecsv_file_name = dt_ref.strftime(isodate_format_file) + '_RMS_' + met.station_id + ".ecsv"

        ffname = os.path.basename(met.ff_name)
        platepar = platepars_recalibrated_dict[ffname]
        evtdate = datetime.datetime.strptime(ffname[10:29], '%Y%m%d_%H%M%S_%f')

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
        out_str = """# %ECSV 0.9
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
            # Add an entry to the ECSV file
            ra = np.degrees(ra)
            dec = np.degrees(dec)
            azim = np.degrees(azim)
            alt = np.degrees(alt)
            entry = [ptdate.strftime(isodate_format_entry), "{:10.6f}".format(ra),
                "{:+10.6f}".format(dec), "{:10.6f}".format(azim), "{:+10.6f}".format(alt),
                "{:+7.2f}".format(mag), "{:9.3f}".format(x), "{:9.3f}".format(y)]

            out_str += ",".join(entry) + "\n"

        ecsv_file_path = os.path.join(outdir, ecsv_file_name)

        # Write file to disk
        with open(ecsv_file_path, 'w') as f:
            f.write(out_str)

        print("ESCV file saved to:", ecsv_file_path)


if __name__ == '__main__':
    saveECSV(sys.argv[1])
