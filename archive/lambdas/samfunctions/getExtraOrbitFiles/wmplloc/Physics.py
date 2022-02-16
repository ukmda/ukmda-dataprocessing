""" Implementations of frequently used equations. """

from __future__ import print_function, division, absolute_import


import numpy as np
import scipy.interpolate


def calcRadiatedEnergy(time, mag_abs, P_0m=840.0):
    """ Calculate the radiated energy given the light curve.

    Arguments:
        time: [ndarray] Time of individual magnitude measurement (s).
        mag_abs: [nadrray] Absolute magnitudes (i.e. apparent meteor magnitudes @100km).

    Keyword arguments:
        P_0m: [float] Power output of a zero absolute magnitude meteor. 840W by default, as that is the R
            bandpass for a T = 4500K black body meteor. See: Weryk & Brown, 2013 - "Simultaneous radar and 
            video meteors - II. Photometry and ionisation" for more details.

    Return:
        initens_int: [float] Total radiated energy (J).

    """

    # Calculate the intensities from absolute magnitudes
    intens = P_0m*10**(-0.4*mag_abs)

    # Interpolate I
    intens_interpol = scipy.interpolate.PchipInterpolator(time, intens)

    # Integrate the interpolated I
    intens_int = intens_interpol.integrate(np.min(time), np.max(time))

    return intens_int



def calcMass(time, mag_abs, velocity, tau=0.007, P_0m=840.0):
    """ Calculates the mass of a meteoroid from the time and absolute magnitude. 
    
    Arguments:
        time: [ndarray] Time of individual magnitude measurement (s).
        mag_abs: [nadrray] Absolute magnitudes (i.e. apparent meteor magnitudes @100km).
        velocity: [float or ndarray] Average velocity of the meteor, or velocity at every point of the meteor
            in m/s.

    Keyword arguments:
        tau: [float] Luminous efficiency (ratio, not percent!). 0.007 (i.e. 0.7%) by default (Ceplecha & McCrosky, 1976)
        P_0m: [float] Power output of a zero absolute magnitude meteor. 840W by default, as that is the R
            bandpass for a T = 4500K black body meteor. See: Weryk & Brown, 2013 - "Simultaneous radar and 
            video meteors - II. Photometry and ionisation" for more details.

    Return:
        mass: [float] Photometric mass of the meteoroid in kg.

    """

    # Theory:
    # I = P_0m*10^(-0.4*M_abs)
    # M = (2/tau)*integral(I/v^2 dt)

    # Compute the radiated energy
    intens_int = calcRadiatedEnergy(time, mag_abs, P_0m=P_0m)

    # Calculate the mass
    mass = (2.0/(tau*velocity**2))*intens_int

    return mass

