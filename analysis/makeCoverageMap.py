#
# Google maps with python
#
import sys
import os
import configparser
import gmplot
import xmltodict
import glob
from cryptography.fernet import Fernet


def munchKML(fname):
    with open(fname) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        lats = []
        lngs = []
        for lin in coords:
            s = lin.split(',')
            lngs.append(float(s[0]))
            lats.append(float(s[1]))

    return cname, lats, lngs


def decodeApiKey(enckey):
    key = open(os.path.expanduser("~/.ssh/gmap.key"), "rb").read()
    f = Fernet(key)
    apikey = f.decrypt(enckey.encode('utf-8'))
    return apikey.decode('utf-8')


if __name__ == '__main__':
    kmlsource = sys.argv[2]
    outdir = sys.argv[3]

    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    apikey = decodeApiKey(config['maps']['apikey'])

    gmap = gmplot.GoogleMapPlotter(52, -1.0, 5, apikey=apikey, 
        title='Camera Coverage', map_type='satellite')


    for fn in glob.glob1(kmlsource, '*.kml'):
        cn, lats, lngs = munchKML(os.path.join(kmlsource,fn))
        gmap.polygon(lats, lngs, color='cornflowerblue', edge_width=1)

    # Draw the map to an HTML file:
    gmap.draw(os.path.join(outdir, 'coverage.html'))
