# 
# 
#
#from genericpath import exists
import os
import sys
import numpy as np
import datetime 
import json
import glob
import shutil

from wmpl.Utils.TrajConversions import geo2Cartesian, raDec2AltAz, altAz2RADec, \
    raDec2ECI, datetime2JD
from wmpl.Utils.Math import vectNorm, angleBetweenVectors, vectorFromPointDirectionAndAngle
from wmpl.Utils.Earth import greatCircleDistance


def checkFOVOverlap(rp, tp):
    """ Check if two stations have overlapping fields of view between heights of 50 to 115 km.
    
    Arguments:
        rp: [Platepar] Reference platepar.
        tp: [Platepar] Test platepar.

    Return:
        [bool] True if FOVs overlap, False otherwise.
    """
    # reject stations that are in the same location
    
    stat_dist = greatCircleDistance(np.radians(rp.lat),np.radians(rp.lon),np.radians(tp.lat),np.radians(tp.lon))
    if stat_dist < 5.0 or stat_dist > 600: 
        #print('stations too close together')
        return False

    # Compute the FOV diagonals of both stations
    reference_fov = np.radians(np.sqrt(rp.fov_v**2 + rp.fov_h**2))
    test_fov = np.radians(np.sqrt(tp.fov_v**2 + tp.fov_h**2))


    lat1, lon1, elev1 = np.radians(rp.lat), np.radians(rp.lon), rp.elev
    lat2, lon2, elev2 = np.radians(tp.lat), np.radians(tp.lon), tp.elev

    # Compute alt/az of the FOV centre
    azim1, alt1 = raDec2AltAz(np.radians(rp.RA_d), np.radians(rp.dec_d), rp.JD, lat1, lon1)
    azim2, alt2 = raDec2AltAz(np.radians(tp.RA_d), np.radians(tp.dec_d), tp.JD, lat2, lon2)

    # Use now as a reference time for FOV overlap check
    ref_jd = datetime2JD(datetime.datetime.utcnow())

    # Compute ECI coordinates of both stations
    reference_stat_eci = np.array(geo2Cartesian(lat1, lon1, elev1, ref_jd))
    test_stat_eci = np.array(geo2Cartesian(lat2, lon2, elev2, ref_jd))

    # Compute ECI vectors of the FOV centre
    ra1, dec1 = altAz2RADec(azim1, alt1, ref_jd, lat1, lon1)
    reference_fov_eci = vectNorm(np.array(raDec2ECI(ra1, dec1)))
    ra2, dec2 = altAz2RADec(azim2, alt2, ref_jd, lat2, lon2)
    test_fov_eci = vectNorm(np.array(raDec2ECI(ra2, dec2)))

    # Compute ECI coordinates at different heights along the FOV line and check for FOV overlap
    # The checked heights are 50, 70, 95, and 115 km (ordered by overlap probability for faster 
    # execution)
    for height_above_ground in [95000, 70000, 115000, 50000]:

        # Compute points in the middle of FOVs of both stations at given heights
        reference_fov_point = reference_stat_eci + reference_fov_eci*(height_above_ground
            - elev1)/np.sin(alt1)
        test_fov_point = test_stat_eci + test_fov_eci*(height_above_ground - elev2)/np.sin(alt2)

        # Check if the middles of the FOV are in the other camera's FOV
        if (angleBetweenVectors(reference_fov_eci, test_fov_point - reference_stat_eci) <= reference_fov/2) \
            or (angleBetweenVectors(test_fov_eci, reference_fov_point - test_stat_eci) <= test_fov/2):

            return True

        # Compute vectors pointing from one station's point on the FOV line to the other
        reference_to_test = vectNorm(test_fov_point - reference_fov_point)
        test_to_reference = -reference_to_test

        # Compute vectors from the ground to those points
        reference_fov_gnd = reference_fov_point - reference_stat_eci
        test_fov_gnd = test_fov_point - test_stat_eci

        # Compute vectors moved towards the other station by half the FOV diameter
        reference_moved = reference_stat_eci + vectorFromPointDirectionAndAngle(reference_fov_gnd,
            reference_to_test, reference_fov/2)
        test_moved = test_stat_eci + vectorFromPointDirectionAndAngle(test_fov_gnd, test_to_reference,
            test_fov/2)

        # Compute the vector pointing from one station to the moved point of the other station
        reference_to_test_moved = vectNorm(test_moved - reference_stat_eci)
        test_to_reference_moved = vectNorm(reference_moved - test_stat_eci)


        # Check if the FOVs overlap
        if (angleBetweenVectors(reference_fov_eci, reference_to_test_moved) <= reference_fov/2) \
            or (angleBetweenVectors(test_fov_eci, test_to_reference_moved) <= test_fov/2):

            return True


    return False


class PlatePar():
    def __init__(self, fldr, camid):
        platepar_path = os.path.join(fldr, camid+'.json')
        with open(platepar_path, 'r') as f:
            data = " ".join(f.readlines())
        self.__dict__ = json.loads(data)

        # Station coordinates
        self.lat = self.__dict__['lat']
        self.lon = self.__dict__['lon']
        self.elev = self.__dict__['elev']

        # Reference time and date
        self.time = 0
        self.JD = self.__dict__['JD']

        # UT correction
        self.UT_corr =self.__dict__['UT_corr']

        self.Ho = self.__dict__['Ho']
        self.X_res = self.__dict__['X_res']
        self.Y_res = self.__dict__['Y_res']

        self.fov_h = self.__dict__['fov_h']
        self.fov_v = self.__dict__['fov_v']

        # FOV centre
        self.RA_d = self.__dict__['RA_d']
        self.dec_d = self.__dict__['dec_d']
        self.pos_angle_ref = self.__dict__['pos_angle_ref']
        self.rotation_from_horiz = self.__dict__['rotation_from_horiz']

        self.az_centre = self.__dict__['az_centre']
        self.alt_centre = self.__dict__['alt_centre']

        # FOV scale (px/deg)
        self.F_scale = self.__dict__['F_scale']


def getOverlappingCameras(srcfolder):

    pplist = glob.glob1(srcfolder, "*.json")
    pplist2 = pplist
    matches = []

    for refppfil in pplist:
        currmatches=[]
        refcam,_ = os.path.splitext(refppfil)
        currmatches.append(refcam)
        refpp = PlatePar(srcfolder, refcam)
        #print('checking ', refcam)
        for testppfil in pplist2:
            if testppfil != refppfil:
                testcam,_ = os.path.splitext(testppfil)
                testpp = PlatePar(srcfolder, testcam)
                #print('comparing to ', testcam)
                if checkFOVOverlap(refpp, testpp) is True:
                    currmatches.append(testcam)
        matches.append(currmatches)

    return matches



if __name__ == '__main__':
    #pp1 = PlatePar('f:/videos/meteorcam/ukmondata/platepars',sys.argv[1])
    #pp2 = PlatePar('f:/videos/meteorcam/ukmondata/platepars',sys.argv[2])
    #if checkFOVOverlap(pp1, pp2) is True:
    #    print('Fov Overlap')
    #else:
    #    print('no overlap')
    src = sys.argv[1]
    targ = sys.argv[2]
    matches = getOverlappingCameras(src)
    for li in matches:
        targpth = os.path.join(targ, li[0])

        if not os.path.exists(targpth):
            os.mkdir(targpth)
        files=glob.glob(targpth)
        for f in files:
            os.remove(f)

        for cam in li:
            try: 
                srcfil = os.path.join(targ, cam + '-100km.kml')
                shutil.copy(srcfil, targpth)
            except:
                srcfil = os.path.join(targ, cam + '.kml')
                shutil.copy(srcfil, targpth)

    #print(matches)
