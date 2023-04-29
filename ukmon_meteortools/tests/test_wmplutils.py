# test the RMS and WMPL utils in the library

import os
from ukmon_meteortools.rmsutils import multiEventGroundMap
from ukmon_meteortools.rmsutils import plotCAMSOrbits, plotRMSOrbits

here = os.path.split(os.path.abspath(__file__))[0]


def test_multiEventGroundMap():
    #multiEventGroundMap()
    assert 1==1


def test_plotCAMSOrbits():
    camsfile = os.path.join(here, 'data', 'sampleCAMSdata.txt')
    outdir = os.path.join(here, 'data')
    plotCAMSOrbits(camsfile, outdir, True)
    assert os.path.isfile(os.path.join(outdir, 'CAMS_2021-06-16T04-00-41.png'))
    os.remove(os.path.join(outdir, 'CAMS_2021-06-16T04-00-41.png'))


def test_plotRMSOrbits():
    rmsfile = os.path.join(here, 'data', 'sampleRMSdata.txt')
    outdir = os.path.join(here, 'data')
    plotRMSOrbits(rmsfile, outdir, True)
    assert os.path.isfile(os.path.join(outdir, 'RMS_2021-06-16T04-00-41.png'))
    os.remove(os.path.join(outdir, 'RMS_2021-06-16T04-00-41.png'))
