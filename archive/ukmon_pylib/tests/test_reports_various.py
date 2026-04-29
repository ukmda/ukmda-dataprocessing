# Copyright (C) 2018-2023 Mark McIntyre

import os

from reports.createSummaryTable import createSummaryTable


here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('DATADIR', default=os.path.join(here, 'data'))


def test_createSummaryTable():
    yr=2023
    createSummaryTable(curryr=None, datadir=datadir)
    fname = os.path.join(datadir,'reports',str(yr), 'summarytable.js')
    assert os.path.isfile(fname)
    lis = open(fname, 'r').readlines()
    assert 'cell.innerHTML = ' in lis[9]
    os.remove(fname)
