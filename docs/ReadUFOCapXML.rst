Class ReadUFOCapXML
===================

NAME
    ReadUFOCapXML - # Python class to parse a UFOCapture XML files

CLASSES
    class UCXml()
     |  UCXml(fname)
     |      construct the object from a file
     |
     |  Methods 
     |  
     |  getCameraDetails()
     |      Returns the fps,cx and cy of the camera
     |  getDate()
     |      Returns the date as an integer YYYYMMDD
     |  getDateStr()
     |      Returens the date as a string YYYY-MM-DD
     |  getDateYMD()
     |      Returns the date as three values Y, M, D
     |  getHits()
     |      Returns the number of frames containing Data
     |  getPaths(fno)
     |      Returns the details of a specific frame 
     |      fno, ono, pixel, bmax, x, y
     |  getStationDetails()
     |      returns the sation name, LID, SID, and geographic location
     |      sta, lid, sid, lat, lng, alt
     |  getTime()
     |      Gets the time of the event in seconds from midnight
     |  getTimeHMS()
     |      Gets the H, M, S of the event
     |  getTimeStr()
     |      Gets the time as a string HH:MM:SS.sss

