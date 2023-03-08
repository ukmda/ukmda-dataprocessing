# Copyright (C) 2018-2023 Mark McIntyre
#
# python code to read in an FTPdetect file and plot all the detections
#

import sys 
import os
import configparser as cr 
from matplotlib import pyplot as plt


def readFTPfile(filename, h):
    events = []
    with open(filename) as f:
        # Skip the header
        for i in range(11):
            next(f)

        for line in f:
            line = line.replace('\n', '').replace('\r', '')
            # The separator marks the beginning of a new meteor
            if "-------------------------------------------------------" in line:
                # Skip the event header
                for i in range(2):
                    next(f)
            # read line containing detail of this event
            line = f.readline()
            rows = int(line.split()[2])
            xvals=[]
            yvals=[]
            # now read in the data of interest
            for r in range(rows):
                line = f.readline()
                _, x, y, _, _, _, _, _ = list(map(float, line.split()[:8]))
                xvals.append(x)
                yvals.append(h-y)
            dta = {'x': xvals, 'y': yvals}
            events.append(dta)

    return events


if __name__ == '__main__':
    config = cr.ConfigParser()
    pth, _ = os.path.split(sys.argv[1])
    config.read(os.path.join(pth, '.config'))
    if len(config) == 1: 
        width=1280
        height=720
    else:
        width = int(config['Capture']['width'])
        height = int(config['Capture']['height'])
    print('plotting field of view {}x{}'.format(width, height))
    events = readFTPfile(sys.argv[1], height)
    for ev in events: 
        plt.plot(ev['x'],ev['y'])
    plt.show()
    spls = sys.argv[1].split('_')
    outfname = f'{spls[1]}_{spls[2]}_{spls[3]}_{spls[3]}_ftpmap.png'
    plt.savefig(outfname)
    plt.close()
