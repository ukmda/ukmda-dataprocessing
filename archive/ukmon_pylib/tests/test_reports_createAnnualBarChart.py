# Copyright (C) 2018-2023 Mark McIntyre

import os

from reports.createAnnualBarChart import createBarChart


here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('DATADIR', default=os.path.join(here, 'data'))


def test_createBarChart():
    # pass year only
    yr=2023
    res = createBarChart(yr=yr)
    assert res is not None

    # pass year and datadir
    res = createBarChart(datadir=datadir, yr=yr)
    outf=os.path.join(datadir, f'Annual-{yr}.jpg')
    print(f'looking for {outf}')
    assert os.path.isfile(outf)
    os.remove(outf)

    # pass datadir only - will fail if we're not in 2023
    res = createBarChart(datadir=datadir, yr=None)
    outf=os.path.join(datadir, f'Annual-{yr}.jpg')
    print(f'looking for {outf}')
    assert os.path.isfile(outf) is False
    try:
        os.remove(outf)
        assert 1==0
    except Exception:
        pass

    # no params passed
    res = createBarChart()
    outf=os.path.join(datadir, f'Annual-{yr}.jpg')
    print(f'looking for {outf}')
    assert os.path.isfile(outf) is False
    try:
        os.remove(outf)
        assert 1==0
    except Exception:
        pass

    # nonexistent year
    res = createBarChart(yr=2150)
    assert res is None
