import sys
import csv
from matplotlib import pyplot as plt
import numpy as np

from wmpl.Utils.Earth import greatCircleDistance


def trackToDistvsHeight(trackcsvfile):
    inputfile = csv.reader(open(trackcsvfile))
    dists = []
    alts = []
    lat0 = -99   # use impossible value
    lng0 = 0
    for row in inputfile:
        #columns are lat, long, height, times
        if row[0] == 'lats': 
            continue
        if lat0 == -99:
            lat0 = np.radians(float(row[0]))
            lng0 = np.radians(float(row[1]))
            dist = 0
        else:
            lat = np.radians(float(row[0]))
            lng = np.radians(float(row[1]))
            dist = greatCircleDistance(lat0, lng0, lat, lng)
        dists.append(dist)
        alt = float(row[2])/1000
        alts.append(alt)
    plt.clf()
    plt.plot(dists,alts)
    outname = trackcsvfile.replace('.csv','_dist_alt.png')
    plt.savefig(outname)
    plt.close()


def trackToTimevsVelocity(trackcsvfile):
    inputfile = csv.reader(open(trackcsvfile))
    dists = []
    tims = []
    lat0 = -99   # use impossible value
    lng0 = 0
    for row in inputfile:
        #columns are lat, long, height, times
        if row[0] == 'lats': 
            continue
        if lat0 == -99:
            lat0 = np.radians(float(row[0]))
            lng0 = np.radians(float(row[1]))
            dist = 0
        else:
            lat = np.radians(float(row[0]))
            lng = np.radians(float(row[1]))
            dist = greatCircleDistance(lat0, lng0, lat, lng)
        dists.append(dist)
        tim = float(row[3])
        tims.append(tim)
    vels=[]
    vels.append(0)
    for i in range(1,len(tims)):
        vel = (dists[i]-dists[i-1])/(tims[i]-tims[i-1])
        print(vel)
        vels.append(vel)
    plt.clf()
    plt.plot(tims,vels)
    outname = trackcsvfile.replace('.csv','_tim_vel.png')
    plt.savefig(outname)
    plt.close()


def trackToTimevsHeight(trackcsvfile):
    inputfile = csv.reader(open(trackcsvfile))
    tims = []
    alts = []
    for row in inputfile:
        #columns are lat, long, height, times
        if row[0] == 'lats': 
            continue
        tims.append(float(row[3]))
        alts.append(float(row[2])/1000)
    plt.clf()
    plt.plot(tims,alts)
    outname = trackcsvfile.replace('.csv','_time_alt.png')
    plt.savefig(outname)
    plt.close()


if __name__ == '__main__':
    trackToTimevsHeight(sys.argv[1])
    trackToDistvsHeight(sys.argv[1])
    trackToTimevsVelocity(sys.argv[1])