ReadUFOAnalyzerXML
==================

NAME
    ReadUFOAnalyzerXML - # class to handle UFO Analyser xml files

CLASSES
    class UAXml(builtins.object)
     |  UAXml(fname)
     |  
     |      Construct the object from a filename
     |      
     |      Arguments:
     |          fname string -- The full path and filename to the XML file
     |  
     |  getCameraDetails()
     |      Get basic camera details
     |      
     |      Returns:
     |          float -- frames per second
     |          float -- horizontal resolution cx
     |          float -- vertical resolution cy
     |  
     |  getDate()
     |      Get the event date as an int
     |      
     |      Returns:
     |          int -- date as YYYYMMDD
     |  
     |  getDateStr()
     |      get the event date as a string 
     |      
     |      Returns:
     |          string -- YYYY-MM-DD
     |  
     |  getDateYMD()
     |      Get the event date as a tuple y,n,d
     |      
     |      Returns:
     |          int -- year
     |          int -- month
     |          int -- day
     |  
     |  getObjectBasics(objno)
     |      Get basic details about an object
     |      
     |      Arguments:
     |          objno int -- the object number zero based
     |      
     |      Returns:
     |          float -- duration in seconds
     |          float -- angular velocity
     |          int -- pix count
     |          float -- max brightness
     |          float -- magnitude estimate
     |          int -- number of frames with a moving object in
     |  
     |  getObjectCount()
     |      Returns the number of objects in this file
     |      
     |      Returns:
     |          int - number of objects
     |  
     |  getObjectEnd(objno)
     |      Get the details of the end point of an object
     |      
     |      Arguments:
     |          objno int -- object to retrieve
     |      
     |      Returns:
     |          floats - ra, dec, height, distance, latitude and longitude
     |  
     |  getObjectFrameDetails(objno, fno)
     |      Get details of a specific frame 
     |      
     |      Arguments:
     |          objno int -- object number
     |          fno int -- frame number 
     |      
     |      Returns:
     |          float -- frame no,ra, dec, magnitude, az, ev, total brightness
     |          int -- b
     |  
     |  getObjectStart(objno)
     |      Get the details of the start point of an object
     |      
     |      Arguments:
     |          objno int -- object to retrieve
     |      
     |      Returns:
     |          floats - ra, dec, height, distance, latitude and longitude
     |  
     |  getProfDetails()
     |      Get details of the profile used to determine the track
     |      
     |      Returns:
     |          float -- azimuth, elevation and rotation
     |          float -- horizontal field of view in degrees
     |          float -- yx, dz, dy (some fit parameters)
     |          float -- number of linked stars
     |  
     |  getStationDetails()
     |      Get station details
     |      
     |      Returns:
     |          string -- station name eg TACKLEY_TC
     |          string -- LID eg TACKLEY
     |          string -- SID eg TC
     |          float -- latitude
     |          float -- longitude (W negative)
     |          float -- altitude (metres)
     |  
     |  getTime()
     |      Get the time as a number of seconds since midnight
     |      
     |      Returns:
     |          int -- secs
     |  
     |  getTimeHMS()
     |      Get time as H,M and S
     |      
     |      Returns:
     |          int -- hour
     |          int -- minute
     |          float -- seconds and milliseconds
     |  
     |  getTimeStr()
     |      Get time as a string
     |      
     |      Returns:
     |          string -- hh:mm:ss.sss
     |  

FILE
    readufoanalyzerxml.py


