# Copyright (C) 2018-2023 Mark McIntyre

#
# python code to plot orbits given a CAMS style Orbit Info file
#

import sys
import os
from datetime import datetime
from wmpl.Utils.PlotOrbits import plotOrbits
import matplotlib.pyplot as plt


def processFile(inf, outdir):
    evttime = datetime.now()

    # read in the data file as a list of lines
    with open(inf, 'r') as src:
        lis = src.readlines()
    
    # create an empty array to contain the orbital elements
    orb_elements=[]

    # ignore the first two lines, split the remaining lines up and find the 
    # elements we want
    for i in range(3,len(lis)):
        li = lis[i].split()
        a = float(li[25])
        e = float(li[26])
        if a < 0:
            q = float(li[22])
            if e==1.0:
                e=1.0001
            a = q/(1-e)
        elemline = [a,e,float(li[28]),float(li[30]),float(li[32])]
        # print(elemline)
        # add the elements to the array
        orb_elements.append(elemline)

    # plot and save the orbits
    plotOrbits(orb_elements, evttime, color_scheme='light')
    plt.savefig(os.path.join(outdir, evttime.strftime('%Y%m%d')+'.png'))
    plt.show()
    plt.close()

    return 


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python plotCAMSOrbits source_file target_folder')

    processFile(sys.argv[1], sys.argv[2])
