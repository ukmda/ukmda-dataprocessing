# Copyright (C) 2018-2023 Mark McIntyre
#
# Google maps with python
#
import sys
import os
import gmplot
import glob
from cryptography.fernet import Fernet
from utils.kmlHandlers import munchKML


def decodeApiKey(enckey):
    key = open(os.path.expanduser('~/.ssh/gmap.key'), 'rb').read()
    f = Fernet(key)
    apikey = f.decrypt(enckey.encode('utf-8'))
    return apikey.decode('utf-8')


def encodeApiKey(plainkey):
    key = open(os.path.expanduser('~/.ssh/gmap.key'), 'rb').read()
    f = Fernet(key)
    apikey = f.encrypt(plainkey.encode('utf-8'))
    return apikey.decode('utf-8')


def makeCoverageMap(kmlsource, outdir, showMarker=False, useName=False):
    apikey = os.getenv('APIKEY')
    apikey = decodeApiKey(apikey)
    kmltempl = os.getenv('KMLTEMPLATE', default='*70km.kml')
    heightval = kmltempl[1:-4]

    gmap = gmplot.GoogleMapPlotter(52, -1.0, 5, apikey=apikey, 
        title=f'Camera Coverage at {heightval}', map_type='satellite')

    flist = glob.glob1(kmlsource, kmltempl)
    cols = list(gmplot.color._HTML_COLOR_CODES.keys())

    for col, fn in zip(cols,flist):
        cn, lats, lngs = munchKML(os.path.join(kmlsource,fn))
        #print(cn, fn)
        gmap.polygon(lats, lngs, color=col, edge_width=1)
        if showMarker is True:
            gmap.text((max(lats)+min(lats))/2, (max(lngs)+min(lngs))/2, cn)

    # Draw the map to an HTML file:
    if useName is False:
        outfname = f'coverage-{heightval}.html'
        gmap.draw(os.path.join(outdir, outfname))
    else:
        outpth = os.path.split(outdir)[0]
        outfname = os.path.split(outdir)[-1] + '.html'
        #print(outdir, outpth, outfname)
        gmap.draw(os.path.join(outpth, outfname))
    return


def createCoveragePage():
    apikey = os.getenv('APIKEY')
    apikey = decodeApiKey(apikey)
    templdir = os.getenv('TEMPLATES', default='/home/ec2-user/prod/website/templates')
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    with open(os.path.join(templdir, 'coverage-maps.html'), 'r') as inf:
        lis = inf.readlines()
    with open(os.path.join(datadir, 'latest','coverage-maps.html'), 'w') as outf:
        for li in lis:
            outf.write(li.replace('{{MAPSAPIKEY}}', apikey))
    return     


if __name__ == '__main__':
    kmlsource = os.path.normpath(sys.argv[1])
    outdir = os.path.normpath(sys.argv[2])
    if len(sys.argv) > 3:
        showMarker=True
    else:
        showMarker=False
    if len(sys.argv) > 4:
        useName=True
    else:
        useName=False

    makeCoverageMap(kmlsource, outdir, showMarker, useName)
