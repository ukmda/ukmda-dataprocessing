import sys
import csv
import simplekml


def trackCsvtoKML(trackcsvfile):
    inputfile = csv.reader(open(trackcsvfile))
    kml=simplekml.Kml()
    for row in inputfile:
        #columns are lat, long, height, times
        kml.newpoint(name='', coords=[(row[1], row[0], row[2])])
    outname = trackcsvfile.replace('.csv','.kml')
    kml.save(outname)


if __name__ == '__main__':
    trackCsvtoKML(sys.argv[1])
