# Copyright (C) 2018-2023 Mark McIntyre

import os

from reports.createLatestTable import createLatestTable
from reports.createSummaryTable import createSummaryTable


here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.path.join(here, 'data')


def test_createLatestTable():
    outdir = os.path.join(datadir, 'latest')
    os.makedirs(outdir, exist_ok=True)
    jpgfile = os.path.join(datadir, 'latest', 'jpglist.txt')
    res = createLatestTable(jpgfile, outdir)
    assert res is True
    outf = os.path.join(datadir, 'latest', 'uploadtimes.csv')
    assert os.path.isfile(outf)
    lis = open(outf, 'r').readlines()
    assert lis[2] == 'IE000J,2023-05-12T04:58:07.000Z\n'
    os.remove(outf)
    outf = os.path.join(datadir, 'latest', 'reportindex.js')
    assert os.path.isfile(outf)
    lis = open(outf, 'r').readlines()
    assert lis[8] == 'cell.innerHTML = "BE000H<br>Abele_W<br>2023-05-12<br>04:54:26";\n'
    os.remove(outf)
    jpgfile = os.path.join(datadir, 'latest', 'jpglist.notexist')
    res = createLatestTable(jpgfile, outdir)
    assert res is False


def test_createSummaryTable():
    createSummaryTable(curryr=None, datadir=None)
    fname = os.path.join(datadir, 'summarytable.js')
    assert os.path.isfile(fname)
    lis = open(fname, 'r').readlines()
    assert lis[9] == 'cell.innerHTML = "6211";\n'
    os.remove(fname)
