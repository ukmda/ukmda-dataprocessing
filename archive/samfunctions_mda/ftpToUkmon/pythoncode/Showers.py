""" Functions to load the shower catalog. """

from __future__ import print_function, division, absolute_import


import os
import json
import numpy as np

from supportFuncs import geocentricToApparentRadiantAndVelocity
from supportFuncs import jd2SolLonSteyaert


class Shower(object):
    def __init__(self, shower_entry):

        # Indicates wheter the flux parameters are defined (False by default)
        self.flux_entry = False

        self.iau_code = shower_entry[0]
        self.name = shower_entry[1]
        self.name_full = shower_entry[2]

        # Generate a unique integer code based on the IAU code (which may have letters)
        self.iau_code_int_unique = ""
        self.iau_code_int = ""
        for c in str(self.iau_code):
            if c.isdigit():
                self.iau_code_int_unique += c
                self.iau_code_int += c
            else:
                self.iau_code_int_unique += str(ord(c))

        self.iau_code_int = int(self.iau_code_int)
        self.iau_code_int_unique = int(self.iau_code_int_unique)
        

        self.lasun_beg = float(shower_entry[3]) # deg
        self.lasun_max = float(shower_entry[4]) # deg
        self.lasun_end = float(shower_entry[5]) # deg
        self.ra_g = float(shower_entry[6]) # deg
        self.dec_g = float(shower_entry[7]) # deg
        self.dra = float(shower_entry[8]) # deg
        self.ddec = float(shower_entry[9]) # deg
        self.vg = float(shower_entry[10]) # km/s

        # Reference height
        self.ref_height = None

        # Binning parameters for combined flux
        self.flux_binning_params = None


        # Load parameters for flux, if that type of shower entry is loaded
        if len(shower_entry) > 13:

            self.flux_entry = True

            self.flux_year = shower_entry[11]
            self.flux_lasun_peak = float(shower_entry[12])
            self.flux_zhr_peak = float(shower_entry[13])
            self.flux_bp = float(shower_entry[14])
            self.flux_bm = float(shower_entry[15])

            self.population_index = float(shower_entry[16])
            self.mass_index = 1 + 2.5*np.log10(self.population_index)

            ref_ht = float(shower_entry[17])
            if ref_ht > 0:
                self.ref_height = ref_ht

            # Load the flux binning parameters
            flux_binning_params = shower_entry[18].strip()
            if len(flux_binning_params) > 0:

                # Replace all apostrophes with double quotes
                flux_binning_params = flux_binning_params.replace("'", '"')

                # Load JSON as dictionary
                self.flux_binning_params = json.loads(flux_binning_params)


        # Apparent radiant
        self.ra = None # deg
        self.dec = None # deg
        self.v_init = None # m/s
        self.azim = None # deg
        self.elev = None # deg
        self.shower_vector = None


        # Add a vactorized version of computeZHRFloat
        self.computeZHR = np.vectorize(self.computeZHRFloat) 


    def computeApparentRadiant(self, latitude, longitude, jdt_ref, meteor_fixed_ht=100000):
        """ Compute the apparent radiant of the shower at the given location and time.

        Arguments:
            latitude: [float] Latitude of the observer (deg).
            longitude: [float] Longitude of the observer (deg).
            jdt_ref: [float] Julian date.

        Keyword arguments:
            meteor_fixed_ht: [float] Assumed height of the meteor (m). 100 km by default.

        Return;
            ra, dec, v_init: [tuple of floats] Apparent radiant (deg and m/s).

        """


        # Compute the location of the radiant due to radiant drift
        if not np.any(np.isnan([self.dra, self.ddec])):
            
            # Solar longitude difference form the peak
            lasun_diff = (np.degrees(jd2SolLonSteyaert(jdt_ref)) - self.lasun_max + 180) % 360 - 180

            ra_g = self.ra_g + lasun_diff*self.dra
            dec_g = self.dec_g + lasun_diff*self.ddec


        # Compute the apparent radiant - assume that the meteor is directly above the station
        self.ra, self.dec, self.v_init = geocentricToApparentRadiantAndVelocity(ra_g,
            dec_g, 1000*self.vg, latitude, longitude, meteor_fixed_ht,
            jdt_ref, include_rotation=True)

        return self.ra, self.dec, self.v_init


    def computeZHRFloat(self, la_sun):
        """ Compute the ZHR activity of the shower given the solar longitude. Only works for showers which
            have the flux parameters. Only takes floats!

        Arguments:
            la_sun: [float] Solar longitude (degrees).

        Return:
            zhr: [float]
        """

        # This can only be done for showers with the flux parameters
        if not self.flux_entry:
            return None

        # Determine if the given solar longitude is before or after the peak
        angle_diff = (la_sun % 360 - self.flux_lasun_peak + 180 + 360) % 360 - 180

        if angle_diff <= 0:
            b = self.flux_bp
            sign = 1

        else:
            b = self.flux_bm
            sign = -1

            # Handle symmetric activity which is defined as Bm being zero and thus Bp should be used too
            if self.flux_bm == 0:
                b = self.flux_bp

        # Compute the ZHR
        zhr = self.flux_zhr_peak*10**(sign*b*angle_diff)

        return zhr


def loadShowers(dir_path, file_name):
    """ Loads the given shower CSV file. """

    # Older versions of numpy don't have the encoding parameter
    try:
        shower_data = np.genfromtxt(os.path.join(dir_path, file_name), delimiter='|', dtype=None,
            autostrip=True, encoding=None)
    except:
        shower_data = np.genfromtxt(os.path.join(dir_path, file_name), delimiter='|', dtype=None,
            autostrip=True)

    return shower_data
