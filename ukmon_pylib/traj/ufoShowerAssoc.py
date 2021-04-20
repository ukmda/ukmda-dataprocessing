#
#  Derive a single-station shower association for an event
#  using functions in RMS
#
from __future__ import print_function, division, absolute_import

import argparse
import sys
import os
import glob
import numpy as np

import Utils.ShowerAssociation as sa
import RMS.ConfigReader as cr
from RMS.Astrometry.Conversions import jd2Date


siteinfotype = np.dtype([('Site', 'S32'), ('HMS', 'i4'), ('SID', 'S16'), ('LID', 'S6'),
    ('Bri', 'i4')])


def getSiteInfo(ftpdetectinfo_path_list):
    lat = None
    lon = None
    done = False
    for siteinfopath in ftpdetectinfo_path_list:
        siteinfopath = os.path.dirname(siteinfopath)
        try:
            with open(os.path.join(siteinfopath, "CameraSites.txt"), 'r') as statf:
                # skip headers
                li = statf.readline()
                li = statf.readline()
                try:
                    li = statf.readline()
                    line = li.split(' ')
                    lat = float(line[1])
                    lon = -float(line[2])
                    done = True
                except:
                    pass
            if done is True:
                break
        except:
            continue
    return lat, lon


if __name__ == "__main__":

    # COMMAND LINE ARGUMENTS
    # Init the command line arguments parser

    arg_parser = argparse.ArgumentParser(description="Perform single-station established shower association on FTPdetectinfo files.")

    arg_parser.add_argument('ftpdetectinfo_path', nargs='+', metavar='FTPDETECTINFO_PATH', type=str,
        help='Path to one or more FTPdetectinfo files.')

    arg_parser.add_argument('-c', '--config', nargs=1, metavar='CONFIG_PATH', type=str,
        help="Path to a config file which will be used instead of the default one.")

    arg_parser.add_argument('-s', '--shower', metavar='SHOWER', type=str,
        help="Associate just this single shower given its code (e.g. PER, ORI, ETA).")

    arg_parser.add_argument('-x', '--hideplot', action="store_true",
        help="""Do not show the plot on the screen.""")

    arg_parser.add_argument('-y', '--latitude', type=float,
        help="""station latitude in standard coordinates.""")

    arg_parser.add_argument('-z', '--longitude', type=float,
        help="""station longitude in standard coordinates.""")

    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    #########################

    ftpdetectinfo_path = cml_args.ftpdetectinfo_path

    # Apply wildcards to input
    ftpdetectinfo_path_list = []
    for entry in ftpdetectinfo_path:
        ftpdetectinfo_path_list += glob.glob(entry)

    # If therea are files given, notify the user
    if len(ftpdetectinfo_path_list) == 0:
        print('No valid FTPdetectinfo files given!')
        sys.exit()


    # Extract parent directory and station ID from path
    dir_path, ftpdetectinfo_name = os.path.split(ftpdetectinfo_path_list[0])
    spls = ftpdetectinfo_name.split('_')
    statID = spls[1]

    # Load the config file
    config = cr.loadConfigFromDirectory('.config', dir_path)

    if config.stationID != statID:
        # load the camera location details if needed
        print('looking for StationInfo file')
        lat, lon = getSiteInfo(ftpdetectinfo_path_list)
        if lat is not None:
            config.latitude = lat
        if lon is not None:
            config.longitude = lon

        print('Checking commandline args')
        if cml_args.latitude is not None:
            config.latitude = cml_args.latitude
        if cml_args.longitude is not None:
            config.longitude = cml_args.longitude
    else:
        print('using location from config file')
    print('Setting station location to', config.latitude, config.longitude)

    tmppath = ftpdetectinfo_path_list
    # Perform shower association
    associations, shower_counts = sa.showerAssociation(config, tmppath,
        shower_code=cml_args.shower, show_plot=(not cml_args.hideplot), save_plot=True, plot_activity=True)

    # Print results to screen
    if shower_counts:
        print()
        print('Shower ranking:')
        for shower, count in shower_counts:

            if shower is None:
                shower_name = '...'
            else:
                shower_name = shower.name
            print(shower_name, count)

        ftpdetectinfo_base_name = ftpdetectinfo_name.replace('FTPdetectinfo_', '').replace('.txt', '')
        assoc_name = ftpdetectinfo_base_name + '_assocs.txt'
        print('Creating association file')
        with open(os.path.join(dir_path, assoc_name), 'w') as outf:
            for key in associations:
                meteor_obj, shower = associations[key]
                jdt = jd2Date(meteor_obj.jdt_ref, dt_obj=True)
                outf.write('{:s},{:d},{:d},{:d},{:d},{:d},{:.2f},'.format(statID, jdt.year, jdt.month, jdt.day,
                    jdt.hour, jdt.minute, jdt.second + jdt.microsecond / 1000000.0))

                if shower is None:
                    outf.write('SPO\n')
                else:
                    outf.write(shower.name + '\n')
        exit(0)
    else:
        print("No meteors!")
        with open(os.path.join(dir_path, 'nometeors'), 'w') as outf:
            outf.write('no meteors\n')
        exit(1)
