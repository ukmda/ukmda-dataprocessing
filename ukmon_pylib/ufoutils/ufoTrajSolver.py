""" Loading CAMS file products, FTPDetectInfo and CameraSites files, running the
    trajectory solver on loaded data.

"""

from __future__ import print_function, division, absolute_import

import os
import sys
import argparse
import numpy as np

from wmplloc.pickleAnalyser import createAdditionalOutput

from wmpl.Formats.GenericFunctions import addSolverOptions
from wmpl.Formats.Milig import StationData, writeMiligInputFile
from wmpl.Utils.TrajConversions import J2000_JD, date2JD, equatorialCoordPrecession_vect, raDec2AltAz_vect, \
    jd2Date
from wmpl.Trajectory.Trajectory import Trajectory
from wmpl.Trajectory.GuralTrajectory import GuralTrajectory
from wmpl.Utils.Math import angleBetweenSphericalCoords


class MeteorObservation(object):
    """ Container for meteor observations.
        The loaded points are RA and Dec in J2000 epoch, in radians.
    """
    def __init__(self, jdt_ref, station_id, latitude, longitude, height, fps, ff_name=None, isj2000=True):

        self.jdt_ref = jdt_ref
        self.station_id = station_id
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.fps = fps

        self.ff_name = ff_name

        # flag to indicate whether data is as-of-epoch or J2000
        self.isj2000 = isj2000

        self.frames = []
        self.time_data = []
        self.x_data = []
        self.y_data = []
        self.azim_data = []
        self.elev_data = []
        self.ra_data = []
        self.dec_data = []
        self.mag_data = []
        self.abs_mag_data = []

    def addPoint(self, frame_n, x, y, azim, elev, ra, dec, mag):
        """ Adds the measurement point to the meteor.

        Arguments:
            frame_n: [flaot] Frame number from the reference time.
            x: [float] X image coordinate.
            y: [float] X image coordinate.
            azim: [float] Azimuth, J2000 in degrees.
            elev: [float] Elevation angle, J2000 in degrees.
            ra: [float] Right ascension, J2000 in degrees.
            dec: [float] Declination, J2000 in degrees.
            mag: [float] Visual magnitude.

        """

        self.frames.append(frame_n)

        # Calculate the time in seconds w.r.t. to the reference JD
        point_time = float(frame_n) / self.fps

        self.time_data.append(point_time)

        self.x_data.append(x)
        self.y_data.append(y)

        # Angular coordinates converted to radians
        self.azim_data.append(np.radians(azim))
        self.elev_data.append(np.radians(elev))
        self.ra_data.append(np.radians(ra))
        self.dec_data.append(np.radians(dec))
        self.mag_data.append(mag)

    def finish(self):
        """ When the initialization is done, convert data lists to numpy arrays. """

        self.frames = np.array(self.frames)
        self.time_data = np.array(self.time_data)
        self.x_data = np.array(self.x_data)
        self.y_data = np.array(self.y_data)
        self.azim_data = np.array(self.azim_data)
        self.elev_data = np.array(self.elev_data)
        self.ra_data = np.array(self.ra_data)
        self.dec_data = np.array(self.dec_data)
        self.mag_data = np.array(self.mag_data)

        # Sort by frame
        temp_arr = np.c_[self.frames, self.time_data, self.x_data, self.y_data, self.azim_data,
        self.elev_data, self.ra_data, self.dec_data, self.mag_data]
        temp_arr = temp_arr[np.argsort(temp_arr[:, 0])]
        self.frames, self.time_data, self.x_data, self.y_data, self.azim_data, self.elev_data, self.ra_data, \
            self.dec_data, self.mag_data = temp_arr.T

    def __repr__(self):

        out_str = ''

        out_str += 'Station ID = ' + str(self.station_id) + '\n'
        out_str += 'JD ref = {:f}'.format(self.jdt_ref) + '\n'
        out_str += 'DT ref = {:s}'.format(jd2Date(self.jdt_ref,
            dt_obj=True).strftime("%Y/%m/%d-%H%M%S.%f")) + '\n'
        out_str += 'Lat = {:f}, Lon = {:f}, Ht = {:f} m'.format(np.degrees(self.latitude),
            np.degrees(self.longitude), self.height) + '\n'
        out_str += 'FPS = {:f}'.format(self.fps) + '\n'
        out_str += 'J2000 {:s}\n'.format(str(self.isj2000))

        out_str += 'Points:\n'
        out_str += 'Time, X, Y, azimuth, elevation, RA, Dec, Mag:\n'

        for point_time, x, y, azim, elev, ra, dec, mag in zip(self.time_data, self.x_data, self.y_data,
                self.azim_data, self.elev_data, self.ra_data, self.dec_data, self.mag_data):

            if mag is None:
                mag = 0

            out_str += '{:.4f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:+.2f}, {:.2f}\n'.format(point_time,
                x, y, np.degrees(azim), np.degrees(elev), np.degrees(ra), np.degrees(dec), mag)

        return out_str


def loadCameraTimeOffsets(cameratimeoffsets_file_name):
    """ Loads time offsets in seconds from the CameraTimeOffsets.txt file.

    Arguments:
        camerasites_file_name: [str] Path to the CameraTimeOffsets.txt file.

    Return:
        time_offsets: [dict] (key, value) pairs of (station_id, time_offset) for every station.
    """

    time_offsets = {}

    # If the file was not found, skip it
    if not os.path.isfile(cameratimeoffsets_file_name):
        print('The time offsets file could not be found! ', cameratimeoffsets_file_name)
        return time_offsets

    with open(cameratimeoffsets_file_name) as f:

        # Skip the header
        for i in range(2):
            next(f)

        # Load camera time offsets
        for line in f:

            line = line.replace('\n', '')
            line = line.split()

            station_id = line[0].strip()

            # Try converting station ID to integer
            try:
                station_id = int(station_id)
            except:
                pass

            t_offset = float(line[1])

            time_offsets[station_id] = t_offset

    return time_offsets


def loadCameraSites(camerasites_file_name):
    """ Loads locations of cameras from a CAMS-style CameraSites files.

    Arguments:
        camerasites_file_name: [str] Path to the CameraSites.txt file.

    Return:
        stations: [dict] A dictionary where the keys are stations IDs, and values are lists of:
            - latitude +N in radians
            - longitude +E in radians
            - height in meters
    """
    stations = {}

    with open(camerasites_file_name) as f:

        # Skip the fist two lines (header)
        for i in range(2):
            next(f)

        # Read in station info
        for line in f:

            # Skip commended out lines
            if line[0] == '#':
                continue

            line = line.replace('\n', '')

            if line:

                line = line.split()

                station_id, lat, lon, height = line[:4]

                station_id = station_id.strip()

                # Try converting station ID to integer
                try:
                    station_id = int(station_id)
                except:
                    pass

                lat, lon, height = map(float, [lat, lon, height])

                stations[station_id] = [np.radians(lat), np.radians(-lon), height * 1000]

    return stations


def loadFTPDetectInfo(ftpdetectinfo_file_name, stations, time_offsets=None,
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

                isj2000 = True
                # UFO style data is as-of-epoch, not J2000
                if line[:3] == 'UFO':
                    isj2000 = False

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

                        jdt_ref += time_offsets[station_id] / 86400.0

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
                    ff_name=ff_name, isj2000=isj2000)

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

            # Check if the next frame is close to the predicted position ###

            # Compute angular distance between the last 2 points on the first FF
            ang_dist = angleBetweenSphericalCoords(met1.dec_data[-2], met1.ra_data[-2], met1.dec_data[-1],
                met1.ra_data[-1])

            # Compute frame difference between the last frame on the 1st FF and the first frame on the 2nd FF
            df = met2.frames[0] + (256 - met1.frames[-1])

            # Skip the pair if the angular distance between the last and first frames is 2x larger than the
            #   frame difference times the expected separation
            ang_dist_between = angleBetweenSphericalCoords(met1.dec_data[-1], met1.ra_data[-1],
                met2.dec_data[0], met2.ra_data[0])

            if ang_dist_between > 2 * df * ang_dist:
                continue

            # If all checks have passed, merge observations ###

            # Recompute the frames
            frames = 256.0 + met2.frames

            # Recompute the time data
            time_data = frames / met1.fps

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

            # Sort all observations by time
            met1.finish()

            # Indicate that the next observation is to be skipped
            merged_indices.append(i + 1)

        # Removed merged meteors from the list
        meteor_list = [element for i, element in enumerate(meteor_list) if i not in merged_indices]

    return meteor_list


def prepareObservations(meteor_list):
    """ Takes a list of MeteorObservation objects, normalizes all data points to the same reference Julian
        date, precesses the observations from J2000 to the epoch of date.

    Arguments:
        meteor_list: [list] List of MeteorObservation objects

    Return:
        (jdt_ref, meteor_list):
            - jdt_ref: [float] reference Julian date for which t = 0
            - meteor_list: [list] A list a MeteorObservations whose time is normalized to jdt_ref, and are
                precessed to the epoch of date

    """

    if meteor_list:

        # The reference meteor is the one with the first time of the first frame
        ref_ind = np.argmin([met.jdt_ref + met.time_data[0] / 86400.0 for met in meteor_list])
        tsec_delta = meteor_list[ref_ind].time_data[0]
        jdt_delta = tsec_delta / 86400.0

        # Normalize all times to the beginning of the first meteor

        # Apply the normalization to the reference meteor
        meteor_list[ref_ind].jdt_ref += jdt_delta
        meteor_list[ref_ind].time_data -= tsec_delta

        meteor_list_tcorr = []

        for i, meteor in enumerate(meteor_list):

            # Only correct non-reference meteors
            if i != ref_ind:

                # Calculate the difference between the reference and the current meteor
                jdt_diff = meteor.jdt_ref - meteor_list[ref_ind].jdt_ref
                tsec_diff = jdt_diff * 86400.0

                # Normalize all meteor times to the same reference time
                meteor.jdt_ref -= jdt_diff
                meteor.time_data += tsec_diff

            meteor_list_tcorr.append(meteor)

        ######
        # The reference JD for all meteors is thus the reference JD of the first meteor
        jdt_ref = meteor_list_tcorr[ref_ind].jdt_ref

        # Precess observations from J2000 to the epoch of date
        meteor_list_epoch_of_date = []
        for meteor in meteor_list_tcorr:

            if meteor.isj2000 is True:
                print('Precessing', meteor.ff_name, 'to epoch of date')
                jdt_ref_vect = np.zeros_like(meteor.ra_data) + jdt_ref

                # Precess from J2000 to the epoch of date
                ra_prec, dec_prec = equatorialCoordPrecession_vect(J2000_JD.days, jdt_ref_vect, meteor.ra_data,
                    meteor.dec_data)

                meteor.ra_data = ra_prec
                meteor.dec_data = dec_prec

                # Convert preccesed Ra, Dec to altitude and azimuth
                meteor.azim_data, meteor.elev_data = raDec2AltAz_vect(meteor.ra_data, meteor.dec_data, jdt_ref,
                    meteor.latitude, meteor.longitude)
            else:
                print(meteor.ff_name, 'already at epoch of date')

            meteor_list_epoch_of_date.append(meteor)

        return jdt_ref, meteor_list_epoch_of_date

    else:
        return None, None


def solveTrajectoryCAMS(meteor_list, output_dir, solver='original', **kwargs):
    """ Feed the list of meteors in the trajectory solver. """
    # Normalize the observations to the same reference Julian date and precess them from J2000 to the
    # epoch of date
    jdt_ref, meteor_list = prepareObservations(meteor_list)

    if meteor_list is not None:

        # for meteor in meteor_list:
        #    print(meteor)

        # Init the trajectory solver
        if solver == 'original':
            traj = Trajectory(jdt_ref, output_dir=output_dir, meastype=1, **kwargs)

        elif solver.lower().startswith('gural'):
            velmodel = solver.lower().strip('gural')
            if len(velmodel) == 1:
                velmodel = int(velmodel)
            else:
                velmodel = 0

            traj = GuralTrajectory(len(meteor_list), jdt_ref, velmodel=velmodel, meastype=1, verbose=1,
                output_dir=output_dir)

        else:
            print('No such solver:', solver)
            return

        # Add meteor observations to the solver
        for meteor in meteor_list:

            if solver == 'original':

                traj.infillTrajectory(meteor.ra_data, meteor.dec_data, meteor.time_data, meteor.latitude,
                    meteor.longitude, meteor.height, station_id=meteor.station_id,
                    magnitudes=meteor.mag_data)

            elif solver == 'gural':

                traj.infillTrajectory(meteor.ra_data, meteor.dec_data, meteor.time_data, meteor.latitude,
                    meteor.longitude, meteor.height)

        # Solve the trajectory
        traj = traj.run()

        return traj


def cams2MiligInput(meteor_list, file_path):
    """ Writes CAMS data to MILIG input file.

    Arguments:
        meteor_list: [list] A list of MeteorObservation objects.
        file_path: [str] Path to the MILIG input file which will be written.

    Return:
        None
    """

    # Normalize the observations to the same reference Julian date and precess them from J2000 to the
    # epoch of date
    jdt_ref, meteor_list = prepareObservations(meteor_list)

    # Convert CAMS MeteorObservation to MILIG StationData object
    milig_list = []
    for i, meteor in enumerate(meteor_list):

        # Check if the station ID is an integer
        try:
            station_id = int(meteor.station_id)

        except ValueError:
            station_id = i + 1

        # Init a new MILIG meteor data container
        milig_meteor = StationData(station_id, meteor.longitude, meteor.latitude, meteor.height)

        # Fill in meteor points
        for azim, elev, t in zip(meteor.azim_data, meteor.elev_data, meteor.time_data):

            # Convert +E of due N azimuth to +W of due S
            milig_meteor.azim_data.append((azim + np.pi) % (2 * np.pi))

            # Convert elevation angle to zenith angle
            milig_meteor.zangle_data.append(np.pi / 2 - elev)
            milig_meteor.time_data.append(t)

        milig_list.append(milig_meteor)

    # Write MILIG input file
    writeMiligInputFile(jdt_ref, milig_list, file_path)


def computeAbsoluteMagnitudes(traj, meteor_list):
    """ Given the trajectory, compute the absolute mangitude (visual mangitude @100km). """

    # Go though every observation of the meteor
    for i, meteor_obs in enumerate(meteor_list):

        # Go through all magnitudes and compute absolute mangitudes
        if traj is not None:
            for dist, mag in zip(traj.observations[i].model_range, meteor_obs.mag_data):

                # Skip nonexistent magnitudes
                if mag is not None:

                    # Compute the range-corrected magnitude
                    abs_mag = mag + 5 * np.log10((10**5) / dist)

                else:
                    abs_mag = None
                # print(mag, abs_mag, dist)
                meteor_obs.abs_mag_data.append(abs_mag)
        else:
            meteor_obs.abs_mag_data.append(6)


if __name__ == "__main__":
    # COMMAND LINE ARGUMENTS

    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Run the trajectory solver on the given FTPdetectinfo file. It is assumed that only one meteor per file is given.")

    arg_parser.add_argument('ftpdetectinfo_path', nargs=1, metavar='FTP_PATH', type=str,
        help='Path to the FTPdetectinfo file. It is assumed that the CameraSites.txt and CameraTimeOffsets.txt are in the same folder.')

    # Add other solver options
    arg_parser = addSolverOptions(arg_parser, skip_velpart=True)

    arg_parser.add_argument('-p', '--velpart', metavar='VELOCITY_PART',
        help='Fixed part from the beginning of the meteor on which the initial velocity estimation using the sliding fit will start. Default is 0.4 (40 percent), but for noisier data this might be bumped up to 0.5.',
        type=float, default=0.4)

    arg_parser.add_argument('-np', '--noplots', help='Disable plots, just do the maths.', action="store_true")

    # Parse the command line arguments
    print('parsing commandline args')
    cml_args = arg_parser.parse_args()

    #########################

    # Parse command line arguments ###

    ftpdetectinfo_path = os.path.abspath(cml_args.ftpdetectinfo_path[0])

    dir_path = os.path.dirname(ftpdetectinfo_path)

    # Check if the given directory is OK
    if not os.path.isfile(ftpdetectinfo_path):
        print('No such file:', ftpdetectinfo_path)
        sys.exit()
    print('processing', ftpdetectinfo_path)
    max_toffset = None
    if cml_args.maxtoffset:
        max_toffset = cml_args.maxtoffset[0]

    velpart = None
    if cml_args.velpart:
        velpart = cml_args.velpart

    vinitht = None
    if cml_args.vinitht:
        vinitht = cml_args.vinitht[0]

    # Image file type of the plots
    plot_file_type = 'png'

    camerasites_file_name = 'CameraSites.txt'
    cameratimeoffsets_file_name = 'CameraTimeOffsets.txt'

    camerasites_file_name = os.path.join(dir_path, camerasites_file_name)
    cameratimeoffsets_file_name = os.path.join(dir_path, cameratimeoffsets_file_name)

    # Get locations of stations
    stations = loadCameraSites(camerasites_file_name)

    # Get time offsets of cameras
    time_offsets = loadCameraTimeOffsets(cameratimeoffsets_file_name)

    # Get the meteor data
    meteor_list = loadFTPDetectInfo(ftpdetectinfo_path, stations, time_offsets=time_offsets)

    # Assume all entires in the FTPdetectinfo path should be used for one meteor
    # meteor_proc_list = [meteor_list]

    try: 
        #for meteor in meteor_proc_list:
        meteor = meteor_list
        etv = True
        outdir = os.path.join(dir_path, jd2Date(meteor[0].jdt_ref, dt_obj=True).strftime("%Y%m%d-%H%M%S.%f"))
        # Run the trajectory solver
        traj = solveTrajectoryCAMS(meteor, outdir, solver=cml_args.solver, max_toffset=max_toffset,
            monte_carlo=(not cml_args.disablemc), mc_runs=cml_args.mcruns,
            geometric_uncert=cml_args.uncertgeom, gravity_correction=(not cml_args.disablegravity),
            plot_all_spatial_residuals=cml_args.plotallspatial, plot_file_type=cml_args.imgformat,
            show_plots=(not cml_args.hideplots), v_init_part=velpart, v_init_ht=vinitht,
            show_jacchia=cml_args.jacchia, estimate_timing_vel=etv, verbose=False,
            save_results=(not cml_args.noplots))

        createAdditionalOutput(traj, outdir)
        sys.exit(0)
    except Exception:
        print('failed to solve')
        sys.exit(2)