# ukmon_pytools
## Version 2023.04.12

Python tools and utilities to work with meteor data from the UK Meteor Network

Available submodules: 

## fileformats
Handling various file formats:
* CameraDetails         - load and access camera location data via the SiteInfo class
* ftpDetectinfo         - read and write RMS's ftpDetectInfo files
* platepar              - read and write RMS's platepar files
* ReadUFOAnalyzerXML    - read UFO Analyser XML files
* ReadUFOCapXML         - read UFO Capture XML files
* imoWorkingShowerList  - read the IMO working shower list via the IMOShowerList class


## rmsutils
Utilities to handle RMS data. Warning: you'll need RMS installed to use these.
* multiDayRadiant       - create a multi-day radiant map using RMS's ShowerAssociation module
* multiTrackStack       - create a multi-day or camera trackstack 
* multiEventGroundMap   - plot two or more events on a ground map
* plotCAMSOrbits        - read a CAMS-style orbit file and plot it
* plotRMSOrbits         - read an RMS-style set of Orbit data and plot it

## usertools
* apiExampleCode        - examples showing how to use the APIs
* drawFTPfile           - read an FTP file and draw a picture of it
* findNearDuplicates    - search for near duplicates in the orbit database
* getLiveImages         - retrieve images from the livestream (requires access to AWS)
* getOverlappingFOVs    - get a list of cameras whose fields of view overlap
* plotTrack             - plot the track of a meteor in various ways
* retrieveECSV          - retrieve data on a detection in ECSV format. Uses the APIs

## utils
* annotateImage         - add a caption to an image
* convertSolLon         - convert solar longitude to JD or datetime
* getActiveShowers      - obtain a list of showers active at a given date
* getShowerDates        - get the start/peak/end dates of a named shower
* kmlHandlers           - functions to read and write KMLs
* Math                  - a mix of date, maths and physics functions
* sendAnEmail           - uses google's APIs to send a mail
* VectorMaths           - some maths to calculate properties of intersecting vectors

To see what capability is offered by a module do the following
```python
>>>from ukmon_pytools.utils import Math
>>>dir(Math)
['J2000_JD', 'JULIAN_EPOCH', 'MINYEAR', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'altAz2RADec', 'altAz2RADec_vect', 'angleBetweenSphericalCoords', 'calcApparentSiderealEarthRotation', 'calcNutationComponents', 'date2JD', 'datetime', 'datetime2JD', 'equatorialCoordPrecession', 'equatorialCoordPrecession_vect', 'greatCircleDistance', 'jd2Date', 'jd2DynamicalTimeJD', 'jd2LST', 'math', 'np', 'raDec2AltAz', 'raDec2AltAz_vect', 'timedelta']
```

Example usage 
```python
>>>from ukmon_pytools.utils import Math
>>> Math.date2JD(2023,4,11,12,45,9)
2460046.0313541666

>>> Math.jd2LST(2460046.0313541666, lon=-1.31*3.1415/180)
(30.741775497696892, 30.76463863658577)