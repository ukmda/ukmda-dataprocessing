# create a data type for search index
import numpy

# 'eventtime,source,shower,mag,loccam,url,imgs'

searchIdx = numpy.dtype([('Tstamp','f8'),('Src','U16'),('Shwr','U8'),
    ('Mag','f8'),('Loccam','U16'),('URL','U128'), ('Imgs', 'U128')])

# format string for writing back out using numpy.savetxt
searchIdxFmt = '%f,%s,%s,%.4f,%s,%s,%s'
