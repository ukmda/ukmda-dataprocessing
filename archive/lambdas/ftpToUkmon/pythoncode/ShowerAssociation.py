""" Single station shower association. """

from __future__ import absolute_import, division, print_function

import copy
import datetime
import os
import numpy as np


from supportFuncs import datetime2JD, cartesianToPolar, jd2SolLonSteyaert
from supportFuncs import greatCircle, fitGreatCircle, greatCirclePhase
from supportFuncs import filenameToDatetime, readFTPdetectinfo, vectNorm

from supportFuncs import raDec2AltAz, vector2RaDec, raDec2Vector
from supportFuncs import angularSeparation, angularSeparationVect, isAngleBetween
from supportFuncs import EARTH_CONSTANTS

from Showers import loadShowers, Shower


EARTH = EARTH_CONSTANTS()


class MeteorSingleStation(object):
    def __init__(self, station_id, lat, lon, ff_name):
        """ Container for single station observations which enables great circle fitting. 

        Arguments:
            station_id: [str]
            lat: [float] +N latitude (deg).
            lon: [float] +E longitude (deg).
            ff_name: [str] Name of the FF file on which the meteor was recorded.
        """

        self.station_id = station_id
        self.lat = lat
        self.lon = lon
        self.ff_name = ff_name

        self.jd_array = []
        self.ra_array = []
        self.dec_array = []
        self.mag_array = []

        self.cartesian_points = None

        self.normal = None

        self.meteor_begin_cartesian = None
        self.meteor_end_cartesian = None

        self.duration = None

        self.jdt_ref = None

        # Solar longitude of the beginning (degrees)
        self.lasun = None

        # Phases on the great circle of the beginning and the end
        self.gc_beg_phase = None
        self.gc_end_phase = None

        # Approx apparent shower radiant (only for associated meteors)
        self.radiant_ra = None
        self.radiant_dec = None



    def addPoint(self, jd, ra, dec, mag):

        self.jd_array.append(jd)
        self.ra_array.append(ra)
        self.dec_array.append(dec)
        self.mag_array.append(mag)




    def fitGC(self):
        """ Fits great circle to observations. """

        self.cartesian_points = []

        self.ra_array = np.array(self.ra_array)
        self.dec_array = np.array(self.dec_array)

        for ra, dec in zip(self.ra_array, self.dec_array):

            vect = vectNorm(raDec2Vector(ra, dec))

            self.cartesian_points.append(vect)


        self.cartesian_points = np.array(self.cartesian_points)

        # Set begin and end pointing vectors
        self.beg_vect = self.cartesian_points[0]
        self.end_vect = self.cartesian_points[-1]

        # Compute alt of the begining and the last point
        self.beg_azim, self.beg_alt = raDec2AltAz(self.ra_array[0], self.dec_array[0], self.jd_array[0], 
            self.lat, self.lon)
        self.end_azim, self.end_alt = raDec2AltAz(self.ra_array[-1], self.dec_array[-1], self.jd_array[-1],
            self.lat, self.lon)


        # Fit a great circle through observations
        x_arr, y_arr, z_arr = self.cartesian_points.T
        coeffs, self.theta0, self.phi0 = fitGreatCircle(x_arr, y_arr, z_arr)

        # Calculate the plane normal
        self.normal = np.array([coeffs[0], coeffs[1], -1.0])

        # Norm the normal vector to unit length
        self.normal = vectNorm(self.normal)

        # Compute RA/Dec of the normal direction
        self.normal_ra, self.normal_dec = vector2RaDec(self.normal)


        # Take pointing directions of the beginning and the end of the meteor
        self.meteor_begin_cartesian = vectNorm(self.cartesian_points[0])
        self.meteor_end_cartesian = vectNorm(self.cartesian_points[-1])

        # Compute angular distance between begin and end (radians)
        self.ang_be = angularSeparationVect(self.beg_vect, self.end_vect)

        # Compute meteor duration in seconds
        self.duration = (self.jd_array[-1] - self.jd_array[0])*86400.0

        # Set the reference JD as the JD of the beginning
        self.jdt_ref = self.jd_array[0]

        # Compute the solar longitude of the beginning (degrees)
        self.lasun = np.degrees(jd2SolLonSteyaert(self.jdt_ref))



    def sampleGC(self, phase_angles):
        """ Sample the fitted great circle and return RA/dec of points for the given phase angles. 
        
        Arguments:
            phase_angles: [ndarray] An array of phase angles (degrees).

        Return:
            ra, dec: [ndarrays] Arrays of RA and Dec (degrees).
        """


        # Sample the great circle
        x_array, y_array, z_array = greatCircle(np.radians(phase_angles), self.theta0, self.phi0)

        if isinstance(x_array, float):
            x_array = [x_array]
            y_array = [y_array]
            z_array = [z_array]

        # Compute RA/Dec of every points
        ra_array = []
        dec_array = []
        for x, y, z in zip(x_array, y_array, z_array):
            ra, dec = vector2RaDec(np.array([x, y, z]))

            ra_array.append(ra)
            dec_array.append(dec)


        return np.array(ra_array), np.array(dec_array)


    def findGCPhase(self, ra, dec):
        """ Finds the phase of the great circle that is closest to the given RA/Dec. 
    
        Arguments;
            ra: [float] RA (deg).
            dec: [float] Declination (deg).

        Return:
            phase: [float] Phase (deg).
        """

        
        x, y, z = raDec2Vector(ra, dec)
        theta, phi = cartesianToPolar(x, y, z)

        # Find the corresponding phase
        phase = np.degrees(greatCirclePhase(theta, phi, self.theta0, self.phi0))

        return phase



    def angularSeparationFromGC(self, ra, dec):
        """ Compute the angular separation from the given coordinaes to the great circle. 
    
        Arguments;
            ra: [float] RA (deg).
            dec: [float] Declination (deg).

        Return:
            ang_separation: [float] Radiant dsitance (deg).
        """

        ang_separation = np.degrees(abs(np.pi/2 - angularSeparation(np.radians(ra), 
                np.radians(dec), np.radians(self.normal_ra), np.radians(self.normal_dec))))

        return ang_separation




def heightModel(v_init, ht_type='beg'):
    """ Function that takes a velocity and returns an extreme begin/end meteor height that was fit on CAMS
        data.

    Arguments:
        v_init: [float] Meteor initial velocity (m/s).

    Keyword arguments:
        ht_type: [str] 'beg' or 'end'

    Return:
        ht: [float] Height (m).

    """

    def _htVsVelModel(v_init, c, a, b):
        return c + a*v_init + b/(v_init**3)


    # Convert velocity to km/s
    v_init /= 1000

    if ht_type.lower() == 'beg':

        # Begin height fit
        fit_params = [97.8411, 0.4081, -20919.3867]

    else:
        # End height fit
        fit_params = [59.4751, 0.3743, -11193.7365]


    # Compute the height in meters
    ht = 1000*_htVsVelModel(v_init, *fit_params)

    return ht




def estimateMeteorHeight(config, meteor_obj, shower):
    """ Estimate the height of a meteor from single station give a candidate shower. 

    Arguments:
        config: [Config instance]
        meteor_obj: [MeteorSingleStation instance]
        shower: [Shower instance]

    Return:
        (ht_b, ht_e): [tuple of floats] Estimated begin and end heights in meters.
    """

    ### Compute all needed values in alt/az coordinates ###
    
    # Compute beginning point vector in alt/az
    beg_ra, beg_dec = vector2RaDec(meteor_obj.beg_vect)
    beg_azim, beg_alt = raDec2AltAz(beg_ra, beg_dec, meteor_obj.jdt_ref, meteor_obj.lat, meteor_obj.lon)
    beg_vect_horiz = raDec2Vector(beg_azim, beg_alt)

    # Compute end point vector in alt/az
    end_ra, end_dec = vector2RaDec(meteor_obj.end_vect)
    end_azim, end_alt = raDec2AltAz(end_ra, end_dec, meteor_obj.jdt_ref, meteor_obj.lat, meteor_obj.lon)
    end_vect_horiz = raDec2Vector(end_azim, end_alt)

    # Compute radiant vector in alt/az
    radiant_azim, radiant_alt = raDec2AltAz(shower.ra, shower.dec, meteor_obj.jdt_ref, meteor_obj.lat, 
        meteor_obj.lon)
    radiant_vector_horiz = raDec2Vector(radiant_azim, radiant_alt)


    # Reject the pairing if the radiant is below the horizon
    if radiant_alt < 0:
        return -1


    # Get distance from Earth's centre to the position given by geographical coordinates for the 
    #   observer's latitude
    earth_radius = EARTH.EQUATORIAL_RADIUS/np.sqrt(1.0 - (EARTH.E**2)*np.sin(np.radians(config.latitude))**2)

    # Compute the distance from Earth's centre to the station (including the sea level height of the station)
    re_dist = earth_radius + config.elevation

    ### ###


    # Compute the distance the meteor traversed during its duration (meters)
    dist = shower.v_init*meteor_obj.duration

    # Compute the angle between the begin and the end point of the meteor (rad)
    theta_met = np.arccos(np.dot(vectNorm(beg_vect_horiz), vectNorm(end_vect_horiz)))

    # Compute the angle between the radiant vector and the end point (rad)
    theta_beg = np.arccos(np.dot(vectNorm(radiant_vector_horiz), -vectNorm(end_vect_horiz)))

    # Compute the angle between the radiant vector and the begin point (rad)
    theta_end = np.arccos(np.dot(-vectNorm(radiant_vector_horiz), -vectNorm(beg_vect_horiz)))

    # Compute the distance from the station to the begin point (meters)
    dist_beg = dist*np.sin(theta_beg)/np.sin(theta_met)

    # Compute the distance from the station to the end point (meters)
    dist_end = dist*np.sin(theta_end)/np.sin(theta_met)


    # Compute the height of the begin point using the law of cosines
    ht_b = np.sqrt(dist_beg**2 + re_dist**2 - 2*dist_beg*re_dist*np.cos(np.radians(90 + meteor_obj.beg_alt)))
    ht_b -= earth_radius
    ht_b = abs(ht_b)


    # Compute the height of the end point using the law of cosines
    ht_e = np.sqrt(dist_end**2 + re_dist**2 - 2*dist_end*re_dist*np.cos(np.radians(90 + meteor_obj.end_alt)))
    ht_e -= earth_radius
    ht_e = abs(ht_e)


    return ht_b, ht_e




def showerAssociation(config, ftpdetectinfo_list):
    """ Do single station shower association based on radiant direction and height. 
    
    Arguments:
        config: [Config instance]
        ftpdetectinfo_list: [list] A list of paths to FTPdetectinfo files.

    Return:
        - associations: [dict] A dictionary where the FF name and the meteor ordinal number on the FF
            file are keys, and the associated Shower object are values.
    """

    shower_table = loadShowers(config.shower_path, config.shower_file_name)
    shower_list = [Shower(shower_entry) for shower_entry in shower_table]

    # Load FTPdetectinfos
    meteor_data = []
    for ftpdetectinfo_path in ftpdetectinfo_list:

        if not os.path.isfile(ftpdetectinfo_path):
            print('No such file:', ftpdetectinfo_path)
            continue

        meteor_data += readFTPdetectinfo(*os.path.split(ftpdetectinfo_path))

    if not len(meteor_data):
        return {}, []


    # Dictionary which holds FF names as keys and meteor measurements + associated showers as values
    associations = {}

    for meteor in meteor_data:

        ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi, meteor_meas = meteor

        # Skip very short meteors
        if len(meteor_meas) < 4:
            continue

        # Check if the data is calibrated
        if not meteor_meas[0][0]:
            print('Data is not calibrated! Meteors cannot be associated to showers!')
            break


        # Init container for meteor observation
        meteor_obj = MeteorSingleStation(cam_code, config.latitude, config.longitude, ff_name)

        # Infill the meteor structure
        for entry in meteor_meas:
            
            calib_status, frame_n, x, y, ra, dec, azim, elev, inten, mag = entry

            # Compute the Julian data of every point
            jd = datetime2JD(filenameToDatetime(ff_name) + datetime.timedelta(seconds=float(frame_n)/fps))

            meteor_obj.addPoint(jd, ra, dec, mag)

            
        # Fit the great circle and compute the geometrical parameters
        meteor_obj.fitGC()


        # Skip all meteors with beginning heights below 15 deg
        if meteor_obj.beg_alt < 15:
            continue

        
        # Go through all showers in the list and find the best match
        best_match_shower = None
        best_match_dist = np.inf
        for shower in shower_list:

            ### Solar longitude filter
            # If the shower doesn't have a stated beginning or end, check if the meteor is within a preset
            # threshold solar longitude difference
            if np.any(np.isnan([shower.lasun_beg, shower.lasun_end])):

                shower.lasun_beg = (shower.lasun_max - config.shower_lasun_threshold) % 360
                shower.lasun_end = (shower.lasun_max + config.shower_lasun_threshold) % 360


            # Filter out all showers which are not active    
            if not isAngleBetween(np.radians(shower.lasun_beg), np.radians(meteor_obj.lasun), np.radians(shower.lasun_end)):
                continue

            ### ###


            ### Radiant filter ###

            # Assume a fixed meteor height for an approximate apparent radiant
            meteor_fixed_ht = 100000 # 100 km
            shower.computeApparentRadiant(config.latitude, config.longitude, meteor_obj.jdt_ref, 
                meteor_fixed_ht=meteor_fixed_ht)

            # Compute the angle between the meteor radiant and the great circle normal
            radiant_separation = meteor_obj.angularSeparationFromGC(shower.ra, shower.dec)


            # Make sure the meteor is within the radiant distance threshold
            if radiant_separation > config.shower_max_radiant_separation:
                continue


            # Compute angle between the meteor's beginning and end, and the shower radiant
            shower.radiant_vector = vectNorm(raDec2Vector(shower.ra, shower.dec))
            begin_separation = np.degrees(angularSeparationVect(shower.radiant_vector,
                meteor_obj.meteor_begin_cartesian))
            end_separation = np.degrees(angularSeparationVect(shower.radiant_vector,
                meteor_obj.meteor_end_cartesian))


            # Make sure the beginning of the meteor is closer to the radiant than it's end
            if begin_separation > end_separation:
                continue

            ### ###


            ### Height filter ###

            # Estimate the limiting meteor height from the velocity (meters)
            filter_beg_ht = heightModel(shower.v_init, ht_type='beg')
            filter_end_ht = heightModel(shower.v_init, ht_type='end')


            ### Estimate the meteor beginning height with +/- 1 frame, otherwise some short meteor may get
            ###   rejected

            meteor_obj_orig = copy.deepcopy(meteor_obj)

            # Shorter
            meteor_obj_m1 = copy.deepcopy(meteor_obj_orig)
            meteor_obj_m1.duration -= 1.0/config.fps
            meteor_ht_m1 = np.mean(estimateMeteorHeight(config, meteor_obj_m1, shower))

            # Nominal
            meteor_ht = np.mean(estimateMeteorHeight(config, meteor_obj_orig, shower))

            # Longer
            meteor_obj_p1 = copy.deepcopy(meteor_obj_orig)
            meteor_obj_p1.duration += 1.0/config.fps
            meteor_ht_p1 = np.mean(estimateMeteorHeight(config, meteor_obj_p1, shower))


            meteor_obj = meteor_obj_orig


            ### ###

            # If all heights (even those with +/- 1 frame) are outside the height range, reject the meteor
            if ((meteor_ht_p1 < filter_end_ht) or (meteor_ht_p1 > filter_beg_ht)) and \
                    ((meteor_ht < filter_end_ht) or (meteor_ht > filter_beg_ht)) and \
                    ((meteor_ht_m1 < filter_end_ht) or (meteor_ht_m1 > filter_beg_ht)):

                continue

            ### ###


            # Compute the radiant elevation above the horizon
            shower.azim, shower.elev = raDec2AltAz(shower.ra, shower.dec, meteor_obj.jdt_ref,
                config.latitude, config.longitude)


            # Take the shower that's closest to the great circle if there are multiple candidates
            if radiant_separation < best_match_dist:
                best_match_dist = radiant_separation
                best_match_shower = copy.deepcopy(shower)

        # Store the associated shower
        associations[(ff_name, meteor_No)] = [meteor_obj, best_match_shower]


    return associations
