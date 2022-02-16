import numpy as np
from numpy.core.umath_tests import inner1d
import scipy.linalg
from datetime import datetime, timedelta, MINYEAR

# Define Julian epoch
JULIAN_EPOCH = datetime(2000, 1, 1, 12) # J2000.0 noon
J2000_JD = timedelta(2451545) # J2000.0 epoch in julian days


def angleBetweenSphericalCoords(phi1, lambda1, phi2, lambda2):
    return np.arccos(np.sin(phi1)*np.sin(phi2) + np.cos(phi1)*np.cos(phi2)*np.cos(lambda2 - lambda1))


def vectNorm(vect):
    return vect/vectMag(vect)

def vectMag(vect):
    return np.sqrt(inner1d(vect, vect))

def rotateVector(vect, axis, theta):
    rot_M = scipy.linalg.expm(np.cross(np.eye(3), axis/vectMag(axis)*theta))
    return np.dot(rot_M, vect)

def jd2Date(jd, UT_corr=0, dt_obj=False):
    try:
        dt = timedelta(days=jd)
        date = dt + JULIAN_EPOCH - J2000_JD + timedelta(hours=UT_corr) 

    # If the date is out of range (i.e. before year 1) use year 1. This is the limitation in the datetime
    # library. Time handling should be switched to astropy.time
    except OverflowError:
        date = datetime(MINYEAR, 1, 1, 0, 0, 0)

    # Return a datetime object if dt_obj == True
    if dt_obj:
        return date

    return date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond/1000.0


def sollon2jd(Year, Month, Long):

    Long = np.radians(Long)
    N = Year - 2000
    if abs(N) > 100:
        print("Algorithm is not stable for years below 1900 or above 2100")

    JDM0 = 2451182.24736 + 365.25963575 * N
    ApproxJD = date2JD(Year, Month, 15, 12, 0, 0)
    DiffJD = ApproxJD-2451545

    Dt = 1.94330 * np.sin(Long - 1.798135) + 0.01305272 * np.sin(2*Long + 2.634232) + 78.195268 + 58.13165 * Long - 0.0000089408 * DiffJD

    if abs(ApproxJD - (JDM0 + Dt))>50:
        Dt = Dt + 365.2596

    JD1 = JDM0 + Dt

    return JD1

def date2JD(year, month, day, hour, minute, second, millisecond=0, UT_corr=0.0):
    """ Convert date and time to Julian Date in J2000.0. 
    
    Arguments:
        year: [int] year
        month: [int] month
        day: [int] day of the date
        hour: [int] hours
        minute: [int] minutes
        second: [int] seconds

    Kwargs:
        millisecond: [int] milliseconds (optional)
        UT_corr: [float] UT correction in hours (difference from local time to UT)
    
    Return:
        [float] julian date, J2000.0 epoch
    """

    # Convert all input arguments to integer (except milliseconds)
    year, month, day, hour, minute, second = map(int, (year, month, day, hour, minute, second))

    # Create datetime object of current time
    dt = datetime(year, month, day, hour, minute, second, int(millisecond*1000))

    # Calculate Julian date
    julian = dt - JULIAN_EPOCH + J2000_JD - timedelta(hours=UT_corr)
    
    # Convert seconds to day fractions
    return julian.days + (julian.seconds + julian.microseconds/1000000.0)/86400.0

def mergeClosePoints(x_array, y_array, delta, x_datetime=False, method='avg'):
    """ Finds if points have similar sample values on the independant axis x (if they are within delta) and 
        averages all y values.

    Arguments:
        x_array: [list] A list of x values (must be of the same length as y_array!).
        y_array: [list] A list of y values (must be of the same length as x_array!).
        delta: [float] Threshold distance between two points in x to merge them. Can be sampling of data (e.g. 
            half the fps).

    Keyword arguments: 
        x_datatime: [bool] Should be True if X is an array of datetime objects. False by default.
        method: [str] Method of merging: "avg", "max", or "min". "avg" is set by default.

    Return:
        x_final, y_final: [tuple of lists] Processed x and y arrays.

    """

    x_final = []
    y_final = []
    skip = 0

    # Step through all x values
    for i, x in enumerate(x_array):

        if skip > 0:
            skip -= 1
            continue


        # Calculate the difference between this point and all others
        diff = np.abs(x_array - x)

        # Convert the difference to seconds if X array elements are datetime
        if x_datetime:
            diff_iter = (time_diff.total_seconds() for time_diff in diff)
            diff = np.fromiter(diff_iter, np.float64, count=len(diff))


        # Count the number of close points to this element
        count = np.count_nonzero(diff < delta)

        # If there are more than one, average them and put them to the list
        if count > 1:

            skip += count - 1

            # Choose either to take the mean, max, or min of the points in the window
            if method.lower() == "max":
                y = np.max(y_array[i : i + count])

            elif method.lower() == "min":
                y = np.min(y_array[i : i + count])
                
            else:
                y = np.mean(y_array[i : i + count])


        # If there are no close points, add the current point to the list
        else:

            y = y_array[i]


        x_final.append(x)
        y_final.append(y)


    return x_final, y_final
