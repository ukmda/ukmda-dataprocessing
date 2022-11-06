from datetime import datetime, timedelta, MINYEAR
import numpy as np
import scipy
import os
from numpy.core.umath_tests import inner1d
import math

# Define Julian epoch
JULIAN_EPOCH = datetime(2000, 1, 1, 12)  # noon (the epoch name is unrelated)
J2000_JD = timedelta(2451545)  # julian epoch in julian dates


class EARTH_CONSTANTS(object):
    """ Holds Earth's shape and physical parameters. """

    def __init__(self):

        # Earth elipsoid parameters in meters (source: WGS84, the GPS standard)
        self.EQUATORIAL_RADIUS = 6378137.0
        self.POLAR_RADIUS = 6356752.314245
        self.E = math.sqrt(1.0 - self.POLAR_RADIUS**2/self.EQUATORIAL_RADIUS**2)
        self.RATIO = self.EQUATORIAL_RADIUS/self.POLAR_RADIUS
        self.SQR_DIFF = self.EQUATORIAL_RADIUS**2 - self.POLAR_RADIUS**2


EARTH = EARTH_CONSTANTS()


def raDec2AltAz(ra, dec, jd, lat, lon):
    """ Convert right ascension and declination to azimuth (+east of sue north) and altitude. 

    Arguments:
        ra: [float] right ascension in degrees
        dec: [float] declination in degrees
        jd: [float] Julian date
        lat: [float] latitude in degrees
        lon: [float] longitude in degrees

    Return:
        (azim, elev): [tuple]
            azim: [float] azimuth (+east of due north) in degrees
            elev: [float] elevation above horizon in degrees

        """

    # Calculate Local Sidereal Time
    lst = np.radians(JD2LST(jd, lon)[0])

    ra = np.radians(ra)
    dec = np.radians(dec)
    lat = np.radians(lat)
    lon = np.radians(lon)

    # Calculate the hour angle
    ha = lst - ra

    # Constrain the hour angle to [-pi, pi] range
    ha = (ha + np.pi) % (2*np.pi) - np.pi

    # Calculate the azimuth
    azim = np.pi + np.arctan2(np.sin(ha), np.cos(ha)*np.sin(lat) - np.tan(dec)*np.cos(lat))

    # Calculate the sine of elevation
    sin_elev = np.sin(lat)*np.sin(dec) + np.cos(lat)*np.cos(dec)*np.cos(ha)

    # Wrap the sine of elevation in the [-1, +1] range
    sin_elev = (sin_elev + 1) % 2 - 1

    elev = np.arcsin(sin_elev)

    return np.degrees(azim), np.degrees(elev)


def date2JD(year, month, day, hour, minute, second, millisecond=0, UT_corr=0.0):
    """ Convert date and time to Julian Date with epoch J2000.0.
    @param year: [int] year
    @param month: [int] month
    @param day: [int] day of the date
    @param hour: [int] hours
    @param minute: [int] minutes
    @param second: [int] seconds
    @param millisecond: [int] milliseconds (optional)
    @param UT_corr: [float] UT correction in hours (difference from local time to UT)
    @return :[float] julian date, epoch 2000.0
    """

    # Convert all input arguments to integer (except milliseconds)
    year, month, day, hour, minute, second = map(int, (year, month, day, hour, minute, second))

    # Create datetime object of current time
    dt = datetime(year, month, day, hour, minute, second, int(millisecond*1000))

    # Calculate Julian date
    julian = dt - JULIAN_EPOCH + J2000_JD - timedelta(hours=UT_corr)

    # Convert seconds to day fractions
    return julian.days + (julian.seconds + julian.microseconds/1000000.0)/86400.0


def datetime2JD(dt, UT_corr=0.0):
    """ Converts a datetime object to Julian date.
    Arguments:
        dt: [datetime object]
    Keyword arguments:
        UT_corr: [float] UT correction in hours (difference from local time to UT)
    Return:
        jd: [float] Julian date
    """

    return date2JD(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000.0,
                   UT_corr=UT_corr)


def jd2Date(jd, UT_corr=0, dt_obj=False):
    """ Converts the given Julian date to (year, month, day, hour, minute, second, millisecond) tuple.
    Arguments:
        jd: [float] Julian date
    Keyword arguments:
        UT_corr: [float] UT correction in hours (difference from local time to UT)
        dt_obj: [bool] returns a datetime object if True. False by default.
    Return:
        (year, month, day, hour, minute, second, millisecond)
    """

    dt = timedelta(days=jd)

    try:
        date = dt + JULIAN_EPOCH - J2000_JD + timedelta(hours=UT_corr)

    # If the date is out of range (i.e. before year 1) use year 1. This is the limitation in the datetime
    # library. Time handling should be switched to astropy.time
    except OverflowError:
        date = datetime(MINYEAR, 1, 1, 0, 0, 0)

    # Return a datetime object if dt_obj == True
    if dt_obj:
        return date

    return date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond/1000.0


def cartesianToPolar(x, y, z):
    """ Converts 3D cartesian coordinates to polar coordinates. 

    Arguments:
        x: [float] Px coordinate.
        y: [float] Py coordinate.
        z: [float] Pz coordinate.

    Return:
        (theta, phi): [float] Polar angles in radians (inclination, azimuth).

    """

    theta = np.arccos(z)
    phi = np.arctan2(y, x)

    return theta, phi



def polarToCartesian(theta, phi):
    """ Converts 3D spherical coordinates to 3D cartesian coordinates. 

    Arguments:
        theta: [float] Longitude in radians.
        phi: [float] Latitude in radians.

    Return:
        (x, y, z): [tuple of floats] Coordinates of the point in 3D cartiesian coordinates.
    """


    x = np.sin(phi)*np.cos(theta)
    y = np.sin(phi)*np.sin(theta)
    z = np.cos(phi)

    return x, y, z


def angularSeparation(ra1, dec1, ra2, dec2):
    """ Calculates the angle between two points on a sphere. 
    
    Arguments:
        ra1: [float] Right ascension 1 (radians).
        dec1: [float] Declination 1 (radians).
        ra2: [float] Right ascension 2 (radians).
        dec2: [float] Declination 2 (radians).

    Return:
        [float] Angle between two coordinates (radians).
    """

    # Classical method
    return np.arccos(np.sin(dec1)*np.sin(dec2) + np.cos(dec1)*np.cos(dec2)*np.cos(ra2 - ra1))


def greatCirclePhase(theta, phi, theta0, phi0):
    """ Find the phase angle of the point closest to the given point on the great circle. 
    
    Arguments:
        theta: [float] Inclination of the point under consideration (radians).
        phi: [float] Nodal angle of the point (radians).
        theta0: [float] Inclination of the great circle (radians).
        phi0: [float] Nodal angle of the great circle (radians).

    Return:
        [float] Phase angle on the great circle of the point under consideration (radians).
    """

    def _pointDist(x):
        """ Calculates the Cartesian distance from a point defined in polar coordinates, and a point on
            a great circle. """
        
        # Convert the pick to Cartesian coordinates
        point = polarToCartesian(phi, theta)

        # Get the point on the great circle
        circle = greatCircle(x, theta0, phi0)

        # Return the distance from the pick to the great circle
        return np.sqrt((point[0] - circle[0])**2 + (point[1] - circle[1])**2 + (point[2] - circle[2])**2)

    # Find the phase angle on the great circle which corresponds to the pick
    res = scipy.optimize.minimize(_pointDist, 0)

    return res.x



def greatCircle(t, theta0, phi0):
    """ 
    Calculates the point on a great circle defined my theta0 and phi0 in Cartesian coordinates. 
    
    Sources:
        - http://demonstrations.wolfram.com/ParametricEquationOfACircleIn3D/

    Arguments:
        t: [float or 1D ndarray] phase angle of the point in the great circle
        theta0: [float] Inclination of the great circle (radians).
        phi0: [float] Nodal angle of the great circle (radians).
    Return:
        [tuple or 2D ndarray] a tuple of (X, Y, Z) coordinates in 3D space (becomes a 2D ndarray if the input
            parameter t is also a ndarray)
    """


    # Calculate individual cartesian components of the great circle points
    x = -np.cos(t)*np.sin(phi0) + np.sin(t)*np.cos(theta0)*np.cos(phi0)
    y = np.cos(t)*np.cos(phi0) + np.sin(t)*np.cos(theta0)*np.sin(phi0)
    z = np.sin(t)*np.sin(theta0)

    return x, y, z


def fitGreatCircle(x, y, z):
    """ Fits a great circle to points in 3D space. 

    Arguments:
        x: [float] X coordiantes of points on the great circle.
        y: [float] Y coordiantes of points on the great circle.
        z: [float] Z coordiantes of points on the great circle.

    Return: 
        X, theta0, phi0: [tuple of floats] Great circle parameters.
    """

    # Add (0, 0, 0) to the data, as the great circle should go through the origin
    x = np.append(x, 0)
    y = np.append(y, 0)
    z = np.append(z, 0)

    # Fit a linear plane through the data points
    A = np.c_[x, y, np.ones(x.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, z)

    # Calculate the great circle parameters
    z2 = C[0]**2 + C[1]**2

    theta0 = np.arcsin(z2/np.sqrt(z2 + z2**2))
    phi0 = np.arctan2(C[1], C[0])

    return C, theta0, phi0


def filenameToDatetime(file_name):
    """ Converts FF bin file name to a datetime object.

    Arguments:
        file_name: [str] Name of a FF file.

    Return:
        [datetime object] Date and time of the first frame in the FF file.

    """

    # e.g.  FF499_20170626_020520_353_0005120.bin
    # or FF_CA0001_20170626_020520_353_0005120.fits

    file_name = file_name.split('_')

    # Check the number of list elements, and the new fits format has one more underscore
    i = 0
    if len(file_name[0]) == 2:
        i = 1

    date = file_name[i + 1]
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])

    time = file_name[i + 2]
    hour = int(time[:2])
    minute = int(time[2:4])
    seconds = int(time[4:6])

    ms = int(file_name[i + 3])


    return datetime(year, month, day, hour, minute, seconds, ms*1000)


def readFTPdetectinfo(ff_directory, file_name, ret_input_format=False):
    """ Read the CAMS format FTPdetectinfo file. 

    Arguments:
        ff_directory: [str] Directory where the FTPdetectinfo file is.
        file_name: [str] Name of the FTPdetectinfo file.

    Keyword arguments:
        ret_input_format: [bool] If True, the list that can be written back using writeFTPdetectinfo is 
            returned. False returnes the expanded list containing everyting that was read from the file (this
            is the default behavious, thus it's False by default)

    Return:
        [tuple]: Two options, see ret_input_format.
    """

    ff_name = ''


    # Open the FTPdetectinfo file
    with open(os.path.join(ff_directory, file_name)) as f:

        entry_counter = 0
        meteor_list = []
        meteor_meas = []
        cam_code = meteor_No = n_segments = fps = hnr = mle = binn = px_fm = rho = phi = None
        calib_status = 0

        # Skip the header
        for i in range(11):
            next(f)


        for line in f:
            
            line = line.replace('\n', '').replace('\r', '')


            # The separator marks the beginning of a new meteor
            if "-------------------------------------------------------" in line:

                # Add the read meteor info to the final list
                if meteor_meas:
                    meteor_list.append([ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, 
                        px_fm, rho, phi, meteor_meas])

                # Reset the line counter to 0
                entry_counter = 0
                meteor_meas = []


            # Read the calibration status
            if entry_counter == 0:

                if 'Uncalibrated' in line:
                    calib_status = 0

                else:
                    calib_status = 1


            # Read the name of the FF file
            if entry_counter == 1:
                ff_name = line

            # Read the meteor parameters
            if entry_counter == 3:
                cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi = line.split()
                meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi = list(map(float, [meteor_No, 
                    n_segments, fps, hnr, mle, binn, px_fm, rho, phi]))

            # Read meteor measurements
            if entry_counter > 3:
                
                # Skip lines with NaNs for centroids
                if '00nan' in line:
                    continue

                mag = np.nan

                # Read magnitude if it is in the file
                if len(line.split()) > 8:

                    line_sp = line.split()

                    mag = float(line_sp[8])

                # Read meteor frame-by-frame measurements
                frame_n, x, y, ra, dec, azim, elev, inten = list(map(float, line.split()[:8]))

                meteor_meas.append([calib_status, frame_n, x, y, ra, dec, azim, elev, inten, mag])


            entry_counter += 1


        # Add the last entry to the list
        if meteor_meas:
            meteor_list.append([ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, 
                rho, phi, meteor_meas])


        # If the return in the format suitable for the writeFTPdetectinfo function, reformat the output list
        if ret_input_format:

            output_list = []

            for entry in meteor_list:
                ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi, \
                    meteor_meas = entry

                # Remove the calibration status from the list of centroids
                meteor_meas = [line[1:] for line in meteor_meas]

                output_list.append([ff_name, meteor_No, rho, phi, meteor_meas])

            return cam_code, fps, output_list

        else:
            return meteor_list


def vectNorm(vect):
    """ Convert a given vector to a unit vector. """
    return vect/vectMag(vect)


def vectMag(vect):
    """ Calculate the magnitude of the given vector. """
    return np.sqrt(inner1d(vect, vect))


def raDec2Vector(ra, dec):
    """ Convert stellar equatorial coordinates to a vector with X, Y and Z components."""
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)
    xt = math.cos(dec_rad)*math.cos(ra_rad)
    yt = math.cos(dec_rad)*math.sin(ra_rad)
    zt = math.sin(dec_rad)
    return xt, yt, zt


def vector2RaDec(eci):
    """ Convert Earth-centered intertial vector to right ascension and declination. """
    # Normalize the ECI coordinates
    eci = vectNorm(eci)
    # Calculate declination
    dec = np.arcsin(eci[2])
    # Calculate right ascension
    ra = np.arctan2(eci[1], eci[0]) % (2*np.pi)
    return np.degrees(ra), np.degrees(dec)


def isAngleBetween(left, ang, right):
    """ Checks if ang is between the angle on the left and right. """
    if right - left < 0:
        right = right - left + 2*np.pi
    else:
        right = right - left
    if ang - left < 0:
        ang = ang - left + 2*np.pi
    else:
        ang = ang - left
    return ang < right


def angularSeparationVect(vect1, vect2):
    """ Calculates angle between vectors in radians. """
    return np.abs(np.arccos(np.dot(vect1, vect2)))


def jd2SolLonSteyaert(jd):
    """ Convert the given Julian date to solar longitude, J2000.0 epoch. Chris Steyaert method.

    Reference: Steyaert, C. (1991). Calculating the solar longitude 2000.0. WGN, Journal of the International 
        Meteor Organization, 19, 31-34.

    Arguments:
        jd: [float] julian date

    Return:
        [float] solar longitude in radians, J2000.0 epoch

    """

    # Define time constants
    A0 = [334166, 3489, 350, 342, 314, 268, 234, 132, 127, 120, 99, 90, 86, 78, 75, 51, 49, 36, 32, 28, 27, 
        24, 21, 21, 20, 16, 13, 13]

    B0 = [4.669257, 4.6261, 2.744, 2.829, 3.628, 4.418, 6.135, 0.742, 2.037, 1.110, 5.233, 2.045, 3.508, 
        1.179, 2.533, 4.58, 4.21, 2.92, 5.85, 1.90, 0.31, 0.34, 4.81, 1.87, 2.46, 0.83, 3.41, 1.08]

    C0 = [6283.07585, 12566.1517, 5753.385, 3.523, 77713.771, 7860.419, 3930.210, 11506.77, 529.691, 1577.344, 
        5884.927, 26.298, 398.149, 5223.694, 5507.553, 18849.23, 775.52, 0.07, 11790.63, 796.3, 10977.08, 
        5486.78, 2544.31, 5573.14, 6069.78, 213.3, 2942.46, 20.78]

    A1 = [20606, 430, 43]
    B1 = [2.67823, 2.635, 1.59]
    C1 = [6283.07585, 12566.152, 3.52]

    A2 = [872, 29]
    B2 = [1.073, 0.44]
    C2 = [6283.07585, 12566.15]

    A3 = 29
    B3 = 5.84
    C3 = 6283.07585

    # Number of millennia since 2000
    T = (jd - 2451545.0)/365250.0

    # Mean solar longitude
    L0 = 4.8950627 + 6283.07585*T - 0.0000099*T**2

    # Wrap L0 to [0, 2pi] range
    L0 = L0 % (2*np.pi)

    # Periodical terms
    S0 = np.sum([A0[i]*np.cos((B0[i] + C0[i]*T) % (2*np.pi)) for i in range(28)])
    S1 = np.sum([A1[i]*np.cos((B1[i] + C1[i]*T) % (2*np.pi)) for i in range(3)])
    S2 = np.sum([A2[i]*np.cos((B2[i] + C2[i]*T) % (2*np.pi)) for i in range(2)])
    S3 = A3*np.cos((B3 + C3*T) % (2*np.pi))

    # Solar longitude of J2000.0
    L = L0 + (S0 + S1*T + S2*T**2 + S3*T**3)*1e-7

    # Bound to solar longitude to the [0, 2pi] range
    L = L % (2*np.pi)

    return L


class simpleConfig(object):
    """ Holds Earth's shape and physical parameters. """

    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.elevation = None
        self.shower_path = None
        self.shower_file_name = 'established_showers.csv'
        self.shower_lasun_threshold = 2.0
        self.shower_max_radiant_separation = 7.5
        self.fps = 25


def loadConfigFromDirectory(pth, cfgname='.config'):
    cfgobj = simpleConfig()
    cfgfile = os.path.join(pth, cfgname)
    with open(cfgfile, 'r') as inf:
        lis = inf.readlines()
    for li in lis:
        spls = li.split(' ')
        if 'latitude:' in spls[0]:
            cfgobj.latitude = float(spls[1])
        if 'longitude:' in spls[0]:
            cfgobj.longitude = float(spls[1])
        if 'elevation:' in spls[0]:
            cfgobj.elevation = float(spls[1])
        if 'fps:' in spls[0]:
            cfgobj.fps = float(spls[1])
    cfgobj.shower_path = '.'

    return cfgobj


def geocentricToApparentRadiantAndVelocity(ra_g, dec_g, vg, lat, lon, elev, jd, include_rotation=True):

    #print(f'entry ra/dec vg lat lon elev jd {ra_g}, {dec_g}, {vg}, {lat}, {lon}, {elev}, {jd}')
    # Compute ECI coordinates of the meteor state vector
    state_vector = geo2Cartesian(lat, lon, elev, jd)
    eci_x, eci_y, eci_z = state_vector
    # Assume that the velocity at infinity corresponds to the initial velocity
    v_init = np.sqrt(vg**2 + (2*6.67408*5.9722)*1e13/vectMag(state_vector))
    # Calculate the geocentric latitude (latitude which considers the Earth as an elipsoid) of the reference
    # trajectory point
    lat_geocentric = np.degrees(math.atan2(eci_z, math.sqrt(eci_x**2 + eci_y**2)))
    ### Uncorrect for zenith attraction ###
    # Compute the radiant in the local coordinates
    azim, elev = raDec2AltAz(ra_g, dec_g, jd, lat_geocentric, lon)
    #print(lat_geocentric, azim, elev)
    # Compute the zenith angle
    eta = np.radians(90.0 - elev)
    # Numerically correct for zenith attraction
    diff = 10e-5
    zc = eta
    while diff > 10e-6:
        # Update the zenith distance
        zc -= diff
        # Calculate the zenith attraction correction
        delta_zc = 2*math.atan((v_init - vg)*math.tan(zc/2.0)/(v_init + vg))
        diff = zc + delta_zc - eta
    # Compute the uncorrected geocentric radiant for zenith attraction
    #print(zc)
    ra, dec = altAz2RADec(azim, 90.0 - np.degrees(zc), jd, lat_geocentric, lon)
    #print(f'uncorrected ra/dec {ra}, {dec}')
    # Apply the rotation correction
    if include_rotation:
        # Calculate the velocity of the Earth rotation at the position of the reference trajectory point (m/s)
        v_e = 2*math.pi*vectMag(state_vector)*math.cos(np.radians(lat_geocentric))/86164.09053
        # Calculate the equatorial coordinates of east from the reference position on the trajectory
        azimuth_east = 90.0
        altitude_east = 0
        ra_east, dec_east = altAz2RADec(azimuth_east, altitude_east, jd, lat, lon)
        # Compute the radiant vector in ECI coordinates of the apparent radiant
        v_ref_vect = v_init*np.array(raDec2Vector(ra, dec))
        v_ref_nocorr = np.zeros(3)
        # Calculate the derotated reference velocity vector/radiant
        v_ref_nocorr[0] = v_ref_vect[0] + v_e*np.cos(np.radians(ra_east))
        v_ref_nocorr[1] = v_ref_vect[1] + v_e*np.sin(np.radians(ra_east))
        v_ref_nocorr[2] = v_ref_vect[2]
        # Compute the radiant without Earth's rotation included
        ra_norot, dec_norot = vector2RaDec(vectNorm(v_ref_nocorr))
        v_init_norot = vectMag(v_ref_nocorr)
        ra = ra_norot
        dec = dec_norot
        v_init = v_init_norot
    return ra, dec, v_init


def geo2Cartesian(lat, lon, h, julian_date):
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    # Calculate ECEF coordinates
    ecef_x, ecef_y, ecef_z = latLonAlt2ECEF(lat_rad, lon_rad, h)
    # Get Local Sidreal Time
    LST_rad = math.radians(JD2LST(julian_date, np.degrees(lon_rad))[0])
    # Calculate the Earth radius at given latitude
    Rh = math.sqrt(ecef_x**2 + ecef_y**2 + ecef_z**2)
    # Calculate the geocentric latitude (latitude which considers the Earth as an elipsoid)
    lat_geocentric = math.atan2(ecef_z, math.sqrt(ecef_x**2 + ecef_y**2))
    # Calculate Cartesian ECI coordinates (in meters), in the epoch of date
    x = Rh*np.cos(lat_geocentric)*np.cos(LST_rad)
    y = Rh*np.cos(lat_geocentric)*np.sin(LST_rad)
    z = Rh*np.sin(lat_geocentric)
    return x, y, z


def altAz2RADec(azim, elev, jd, lat, lon):
    """ Convert azimuth and altitude in a given time and position on Earth to right ascension and
        declination.
    Arguments:
        azim: [float] azimuth (+east of due north) in degrees
        elev: [float] elevation above horizon in degrees
        jd: [float] Julian date
        lat: [float] latitude of the observer in degrees
        lon: [float] longitde of the observer in degrees
    Return:
        (RA, dec): [tuple]
            RA: [float] right ascension (degrees)
            dec: [float] declination (degrees)
    """
    lst = np.radians(JD2LST(jd, lon)[0])
    
    azim = np.radians(azim)
    elev = np.radians(elev)
    lat = np.radians(lat)
    lon = np.radians(lon)

    ha = math.atan2(-math.sin(azim), math.tan(elev)*math.cos(lat) - math.cos(azim)*math.sin(lat))
    
    # Calculate right ascension
    ra = (lst - ha + 2*np.pi) % (2*np.pi)

    # Calculate declination
    dec = math.asin(math.sin(lat)*math.sin(elev) + math.cos(lat)*math.cos(elev)*math.cos(azim))

    return np.degrees(ra), np.degrees(dec)


def latLonAlt2ECEF(lat, lon, h):
    """ Convert geographical coordinates to Earth centered - Earth fixed coordinates.

    Arguments:
        lat: [float] latitude in radians (+north)
        lon: [float] longitude in radians (+east)
        h: [float] elevation in meters (WGS84)

    Return:
        (x, y, z): [tuple of floats] ECEF coordinates

    """

    # Get distance from Earth centre to the position given by geographical coordinates, in WGS84
    N = EARTH.EQUATORIAL_RADIUS/math.sqrt(1.0 - (EARTH.E**2)*math.sin(lat)**2)

    # Calculate ECEF coordinates
    ecef_x = (N + h)*math.cos(lat)*math.cos(lon)
    ecef_y = (N + h)*math.cos(lat)*math.sin(lon)
    ecef_z = ((1 - EARTH.E**2)*N + h)*math.sin(lat)

    return ecef_x, ecef_y, ecef_z


def JD2LST(julian_date, lon):
    t = (julian_date - J2000_JD.days)/36525.0
    GST = 280.46061837 + 360.98564736629*(julian_date - 2451545) + 0.000387933*t**2 - ((t**3)/38710000)
    GST = (GST + 360) % 360
    LST = (GST + lon + 360) % 360
    return LST, GST
