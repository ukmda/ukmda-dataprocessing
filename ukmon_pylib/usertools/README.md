# usertools

A bunch of scripts that are intended to be used by humans to do interesting stuff.


* drawFTPFile.py - draws a simple line diagram of the detections in an FTP file. Handy for checking for bad masks.
* findNearDuplicates - searches a year's worth of data for possible duplicate trajectories
* getLiveImages - retrieves the live stream data for a specific date/time 
* getOverlappingFovs - identifies overlapping cameras
* manageTraj - routines to delete a duplicate trajectory from the database and/or website
  
Routines intended for use with RMS raw data
* multiDayRadiant
* multiEventGroundMap
* multiTrackStack
* plotShowerInfo


Miscellany
* plotTrack - plot various graphs from a CSV file of x,y,h,t
* plotCAMSOrbits - plot orbits from CAMS data 
* plotRMSOrbits - plot orbits from a bunch of RMS trajectories


Probably Redundant
* compareMLtoManual - compares the results of ML checks to manual checks with CMN_Binviewer
* retrieveECSV - yet another function to grab an ECSV from the database. 
