#
# Python routine to plot stations and vectors on a map of hte UK
#

import numpy as np
import os
import sys
import fnmatch
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

# override PIL's image size limit
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


from fileformats import ReadUFOAnalyzerXML as ua
from fileformats import CameraDetails as cd


def getBearingsForEvent(stns, fldr):
    brngs = np.zeros(len(stns))
    listOfFiles = os.listdir(fldr)
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, '*A.XML'):
            fullname = os.path.join(fldr, entry)
            xmlf = ua.UAXml(fullname)
            sta, _, _, _, _, _ = xmlf.getStationDetails()
            _, _, _, _, _, _, az1, _ = xmlf.getObjectStart(0)
            i = stns.index(sta)
            brngs[i] = az1

        elif entry == 'FTPdetectinfo_UFO.txt':
            with open(os.path.join(fldr, 'FTPdetectinfo_UFO.txt'), 'r') as f:
                lis = f.readlines()
                for s in stns:
                    for j in range(len(lis)):
                        if lis[j][:len(s)] == s:
                            spls = lis[j + 1].split()
                            i = stns.index(s)
                            brngs[i] = spls[5]

    return brngs


def BearingToEndpoint(lat, lon, brng, dist):
    R = 6378.1
    d = dist
    heading_lat1 = np.deg2rad(lat)
    heading_lon1 = np.deg2rad(lon)
    brng = np.deg2rad(brng)

    heading_lat2 = np.arcsin(np.sin(heading_lat1) * np.cos(d / R) + np.cos(heading_lat1) * np.sin(d / R) * np.cos(brng))
    heading_lon2 = heading_lon1 + np.arctan2(np.sin(brng) * np.sin(d / R) * np.cos(heading_lat1),
        np.cos(d / R) - np.sin(heading_lat1) * np.sin(heading_lat2))

    heading_lat2 = np.rad2deg(heading_lat2)
    heading_lon2 = np.rad2deg(heading_lon2)
    return heading_lat2, heading_lon2


def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1, a2, b1, b2])         # s for stacked
    h = np.hstack((s, np.ones((4, 1))))     # h for homogeneous
    l1 = np.cross(h[0], h[1])               # get first line
    l2 = np.cross(h[2], h[3])               # get second line
    x, y, z = np.cross(l1, l2)              # point of intersection
    if z == 0:                              # lines are parallel
        return (float('inf'), float('inf'))
    return (x / z, y / z)


def plotMap(srcpath, intersect):

    lats = []
    longs = []
    stas = []
    if 'camera-details.csv' in srcpath:
        ci = cd.SiteInfo(srcpath)
        ac = ci.getActiveCameras()
        for cam in ac:
            longs.append(cam['Longi'])
            lats.append(cam['Lati'])
            stas.append(cam['CamID'].decode('utf-8'))

    else:
        with open(os.path.join(srcpath, 'CameraSites.txt'), 'r') as f:
            lis = f.readlines()
        for li in lis:
            if li[:1] == '#':
                continue
            dta = li.split(' ')
            stas.append(dta[0])
            lats.append(float(dta[1]))
            longs.append(-float(dta[2]))

    mapproj = ccrs.AlbersEqualArea()
    fig = plt.gcf()
    fig.set_size_inches(16.52, 23.2)

    maxn, minn = max(longs) + 1, min(longs) - 1
    maxa, mina = max(lats) + 1, min(lats) - 1

    plt.title('Station locations')

    ax = plt.axes(projection=mapproj)

    ax.set_extent([minn, maxn, mina, maxa], ccrs.PlateCarree())
#    ax.coastlines(resolution='10m')
#    ax.add_feature(cfeature.OCEAN)
#    ax.add_feature(cfeature.LAND, edgecolor='black')
#    ax.add_feature(cfeature.LAKES, edgecolor='black')
#    ax.add_feature(cfeature.RIVERS)
    ax.gridlines()
    pylib=os.getenv('PYLIB')
    os.environ['CARTOPY_USER_BACKGROUNDS'] = os.path.join(pylib, 'share','maps')
    ax.background_img(name='BM', resolution='low')

    plt.plot(longs, lats, 'bo', markersize=5, linewidth=1, transform=ccrs.PlateCarree())
    for label, xpt, ypt in zip(stas, longs, lats):
        plt.text(xpt, ypt, label, color='red', transform=ccrs.PlateCarree())

    if intersect is True:
        brngs = getBearingsForEvent(stas, srcpath)

        vecs1 = []
        vecs2 = []

        for i in range(len(stas)):
            lat1 = lats[i]
            lon1 = longs[i]
            brng = brngs[i]
            dist = 100
            lat2, lon2 = BearingToEndpoint(lat1, lon1, brng, dist)
            lat = [lat1, lat2]
            lon = [lon1, lon2]
            a1 = [lat1, lon1]
            a2 = [lat2, lon2]
            vecs1.append(a1)
            vecs2.append(a2)

            print(stas[i], lat1, lon1, brng)

            map.plot(lon, lat, 'o-', markersize=5, linewidth=1)

        xi, yi = get_intersect(vecs1[0], vecs2[0], vecs1[1], vecs2[1])
        plt.plot(yi, xi, 'bx', markersize=10, linewidth=1)

    plt.tight_layout()
    datadir = os.getenv('DATADIR')
    if len(datadir) == 0:
        datadir='.'
    plt.savefig(os.path.join(datadir, 'stations.png'), dpi=200)
    plt.show()



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage python plotStationsOnMap.py srcfile optional_intersect')
        print('  will plot all stations in srcfile and optionally the intersections of any events')
    else:
        srcfile = sys.argv[1]
        intersect = False
        if len(sys.argv)>2:
            intersect = True
        plotMap(srcfile, intersect)