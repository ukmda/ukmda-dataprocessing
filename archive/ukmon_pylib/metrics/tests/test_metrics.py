#import pytest
import os
from metrics.costMetrics import getLatestCost

def test_costmetric_total():
    costfile = 'tests/sample.csv'
    outdir = '.'
    accid = '317976261112'

    totcost = getLatestCost(costfile, outdir, accid)
    assert(totcost==1.8049)
    os.remove(f'./costs-{accid}-last.csv')
    return 