#
# Create an annual bar chart of daily matches
#

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime

from wmpl.Utils.TrajConversions import jd2Date


def createBarChart(fname, yr):
    if not os.path.isfile(fname):
        print('{} missing', fname)
        return None
    cols = ['_mjd','_Y_ut']
    matches = pd.read_parquet(fname, columns=cols)
    matches = matches[matches['_Y_ut']==int(yr)]

    matches = matches.sort_values(by=['_mjd'])
    v1=int(matches['_mjd'][0])
    v2=int(matches['_mjd'][len(matches)-1])+2
    ranges=list(range(v1,v2))
    li=matches.groupby(pd.cut(matches['_mjd'], ranges)).count()['_mjd'].tolist()

    dts=[]
    for d in ranges:
        dt = jd2Date(d + 2400000.5, dt_obj=True) # add 2400000.5 to convert to JD
        dts.append(dt)

    fig, ax = plt.subplots()
    width = 0.35       
    nowdt=datetime.datetime.now()
    ax.set_ylabel('# matches')
    ax.set_xlabel('Date')
    ax.set_title('Number of matched events per day. Last updated {}'.format(nowdt.strftime('%Y-%m-%d %H:%M:%S')))

    li.append(0) # comes up one short
    ax.bar(dts, li, width, label='Events')
    fig = plt.gcf()
    fig.set_size_inches(12, 5)
    fig.tight_layout()
    #plt.gca().invert_yaxis()
    plt.savefig('Annual-{}.jpg'.format(yr), dpi=100)

    return matches


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        yr = sys.argv[2]
    else:
        yr=datetime.datetime.now().year
        datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
        fname = os.path.join(datadir, 'matched', 'matches-full-{}.parquet.gzip'.format(yr))
        
    m = createBarChart(fname, yr)
#    print(m.selectByMag(minMag=-2))
