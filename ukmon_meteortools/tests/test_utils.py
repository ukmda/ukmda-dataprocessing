# test cases for the utils package
import datetime
import numpy as np
import os

from ukmon_meteortools.utils import jd2Date, date2JD, datetime2JD, jd2DynamicalTimeJD, jd2LST, sollon2jd, \
    greatCircleDistance, angleBetweenSphericalCoords, calcApparentSiderealEarthRotation, \
    raDec2AltAz, altAz2RADec, \
    getActiveShowers, getShowerDets, getShowerPeak
# getActiveShowersStr, sendAnEmail, \
# calcNutationComponents, equatorialCoordPrecession,  getTrackDetails, getTrajPickle, \
# annotateImage, annotateImageArbitrary

here = os.path.split(os.path.abspath(__file__))[0]


def test_jd2Date():
    dt = jd2Date(2460063.0077546295, dt_obj=True)
    assert (dt - datetime.datetime(2023, 4, 28, 12, 11, 9, microsecond=999987)).total_seconds() < 0.001


def test_date2JD():
    jdt = date2JD(2023, 4, 28, 12, 11, 10)
    assert abs(jdt -2460063.0077546295) < 0.00001


def test_datetime2JD():
    dt = datetime.datetime(2023, 4, 28, 12, 11, 10)
    jdt = datetime2JD(dt)
    assert abs(jdt - 2460063.0077546295) < 0.00001


def test_jd2DynamicalTimeJD():
    dynjdt = jd2DynamicalTimeJD(2460063.0077546295)
    assert abs(dynjdt - 2460063.0085553704) < 0.00001


def test_jd2LST(): 
    lst = jd2LST(2460063.0077546295, np.radians(-2.54))
    assert lst == (38.95722137057129, 39.001552733571955)


def test_sollon2jd():
    jd = sollon2jd(2020, 4, 32.0) # sol lon of lyrids
    assert abs(jd - 2458961.4503479283) < 0.0000001


def test_greatCircleDistance():
    lat1 = np.radians(55.9533)
    lon1 = np.radians(-3.188)
    lat2 = np.radians(48.856)
    lon2 = np.radians(2.352)
    gsd = greatCircleDistance(lat1, lon1, lat2, lon2)
    assert abs(gsd - 873.434938894131) < 0.00001


def test_angleBetweenSphericalCoords():
    p1 = np.radians(55.9533)
    l1 = np.radians(-3.188)
    p2 = np.radians(48.856)
    l2 = np.radians(2.352)
    angl = angleBetweenSphericalCoords(p1, l1, p2, l2)
    assert abs(angl - 0.137095) < 0.0001


def test_calcApparentSiderealEarthRotation():
    jd = 2458961.4503479283
    asr = calcApparentSiderealEarthRotation(jd)
    assert abs(asr - 3.361258) < 0.0001


def test_raDec2AltAz():
    # location of arcturus at 2023-04-29 21:16:02 UT from Oxford
    jd = date2JD(2023,4,29,21,16,2)
    ra = np.radians((14 + 16/60 + 44.67/3600)*15.0) # actual, not J2000
    dec = np.radians(19.0+3/60+31.8/3600) # actual not J2000
    az, alt = raDec2AltAz(ra, dec, jd, lat=np.radians(51.88310), lon=np.radians(-1.30616))
    alt = np.degrees(alt)
    az = np.degrees(az)
    assert abs(az - 122.413) < 0.005  # accurate to about 20 arcsecs
    assert abs(alt - 45.322) < 0.02 # accurate to about 2 arcminutes


def test_altAz2RADec():
    az = np.radians(122 + 24/60 + 46.6/3600)
    alt = np.radians(45 + 19/60 + 21.6/3600)
    jd = date2JD(2023,4,29,21,16,2)
    ra, dec = altAz2RADec(az, alt, jd, lat=np.radians(51.88310), lon=np.radians(-1.30616))
    ra = np.degrees(ra)
    dec = np.degrees(dec)

    assert abs(214.186125 - ra) < 0.01
    assert abs(19.058 - dec) < 0.02


def test_getActiveShowers():
    sl = getActiveShowers(datetime.datetime(2023,4,23,0,0,0),True)
    assert sl == ['LYR', 'ETA']


def test_getQuietActiveShowers():
    sl = getActiveShowers(datetime.datetime(2023,2,23,0,0,0),True)
    assert sl == []


def test_getShowerDets():
    sl = getShowerDets('LYR')
    assert sl == (6, 'April Lyrids', 32.0, '04-22')


def test_getNonExistentShowerDets():
    sl = getShowerDets('XXX')
    assert sl == (0, 'Unknown', 0, 'Unknown')


def test_getShowerPeak():
    sl = getShowerPeak('LYR')
    assert sl == '04-22'


def test_calcNutationComponents():
    # not tested
    assert 1 == 1


def test_equatorialCoordPrecession():
    # not tested
    assert 1 == 1


"""
def test_annotateImage():
def test_annotateImageArbitrary():
def test_getTrackDetails():
def test_getTrajPickle():
def test_sendAnEmail():
"""
