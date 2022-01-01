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
from shapely.geometry import Polygon


def munchKML(fname, return_poly=False):
    with open(fname) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        if return_poly is False:
            lats = []
            lngs = []
            for lin in coords:
                s = lin.split(',')
                lngs.append(float(s[0]))
                lats.append(float(s[1]))
            return cname, lats, lngs
        else:
            ptsarr=[]
            for lin in coords:
                s = lin.split(',')
                ptsarr.append((float(s[0]), float(s[1])))
            polyg = Polygon(ptsarr)
            return cname, polyg 


def decodeApiKey(enckey):
    key = open(os.path.expanduser('~/.ssh/gmap.key'), 'rb').read()
    f = Fernet(key)
    apikey = f.decrypt(enckey.encode('utf-8'))
    return apikey.decode('utf-8')


def makeCoverageMap(config, kmlsource, outdir, showMarker=False, useName=False):
    apikey = decodeApiKey(config['maps']['apikey'])
    kmltempl = config['maps']['kmltemplate']
    #print(apikey)
    gmap = gmplot.GoogleMapPlotter(52, -1.0, 5, apikey=apikey, 
        title='Camera Coverage', map_type='satellite')

    flist = glob.glob1(kmlsource, kmltempl)
    cols = list(gmplot.color._HTML_COLOR_CODES.keys())

    for col, fn in zip(cols,flist):
        cn, lats, lngs = munchKML(os.path.join(kmlsource,fn))
        print(cn, fn)
        gmap.polygon(lats, lngs, color=col, edge_width=1)
        if showMarker is True:
            gmap.text((max(lats)+min(lats))/2, (max(lngs)+min(lngs))/2, cn)

    # Draw the map to an HTML file:
    if useName is False:
        outfname = 'coverage.html'
        gmap.draw(os.path.join(outdir, outfname))
    else:
        outpth = os.path.split(outdir)[0]
        outfname = os.path.split(outdir)[-1] + '.html'
        print(outdir, outpth, outfname)
        gmap.draw(os.path.join(outpth, outfname))
    return


if __name__ == '__main__':
    kmlsource = os.path.normpath(sys.argv[2])
    outdir = os.path.normpath(sys.argv[3])
    if len(sys.argv) > 4:
        showMarker=True
    else:
        showMarker=False
    if len(sys.argv) > 5:
        useName=True
    else:
        useName=False

    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    makeCoverageMap(config, kmlsource, outdir, showMarker, useName)
