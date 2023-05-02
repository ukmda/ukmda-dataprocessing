# Copyright (C) 2018-2023 Mark McIntyre
# flake8: noqa
"""
Utility functions used across the UKMON toolset

List of Functions:  
jd2Date, date2JD, datetime2JD, jd2DynamicalTimeJD, jd2LST, sollon2jd  
greatCircleDistance, angleBetweenSphericalCoords, calcApparentSiderealEarthRotation  
calcNutationComponents, equatorialCoordPrecession,  raDec2AltAz, altAz2RADec  
altAz2RADec_vect, raDec2AltAz_vect, equatorialCoordPrecession_vect  
annotateImage, annotateImageArbitrary  
getActiveShowers, getActiveShowersStr, getShowerDets, getShowerPeak  
trackCsvtoKML, getTrackDetails, getTrajPickle, munchKML  
sendAnEmail  
shortestDistance2Lines  
"""

from .Math import jd2Date, date2JD,datetime2JD, jd2DynamicalTimeJD, JULIAN_EPOCH, J2000_JD, jd2LST
from .Math import greatCircleDistance, angleBetweenSphericalCoords, calcApparentSiderealEarthRotation
from .Math import calcNutationComponents, equatorialCoordPrecession,  raDec2AltAz, altAz2RADec
from .Math import altAz2RADec_vect, raDec2AltAz_vect, equatorialCoordPrecession_vect

from .annotateImage import annotateImage, annotateImageArbitrary

from .convertSolLon import sollon2jd

from .getActiveShowers import getActiveShowers, getActiveShowersStr

from .getShowerDates import getShowerDets, getShowerPeak

from .kmlHandlers import trackCsvtoKML, getTrackDetails, getTrajPickle, munchKML

from .sendAnEmail import sendAnEmail
