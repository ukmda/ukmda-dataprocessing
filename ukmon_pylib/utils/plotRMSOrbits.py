#
# python code to plot orbits given a CAMS style Orbit Info file
#

import sys
import os
import pandas as pd
from datetime import datetime
from wmpl.Utils.PlotOrbits import plotOrbits
import matplotlib.pyplot as plt


def processFile(inf, outdir):
    evttime = datetime.now()

    # read in the data file as a list of lines
    data = pd.read_csv(inf)
    avals = list(data['_a'])    
    evals = list(data['_e'])    
    ivals = list(data['_incl'])    
    wvals = list(data['_peri'])    
    nvals = list(data['_node'])    
    # create an empty array to contain the orbital elements
    orb_elements=[]

    # ignore the first two lines, split the remaining lines up and find the 
    # elements we want
    for i in range(len(avals)):
        if avals[i] > 0 and avals[i]<=10:
            elemline = [avals[i],evals[i],ivals[i],wvals[i],nvals[i]]
            # add the elements to the array
            orb_elements.append(elemline)

    # plot and save the orbits
    plotOrbits(orb_elements, evttime, color_scheme='light')
    plt.savefig(os.path.join(outdir, evttime.strftime('%Y%m%d')+'.png'))
    plt.show()

    return 


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python plotRMSOrbits source_file target_folder')

    processFile(sys.argv[1], sys.argv[2])
