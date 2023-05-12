# tests for createExchangeFiles.py
import datetime
import os

from reports.createExchangeFiles import createDetectionsFile, createEventList, createMatchesFile, \
    createWebpage, createCameraFile

here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.path.join(here, 'data')
targdate = datetime.datetime(2023,5,12)


def test_createDetectionsFile():
    createDetectionsFile(targdate, datadir)
    assert 1==1


def test_createEventList():
    createEventList
    assert 1==1


def test_createMatchesFile():
    createMatchesFile(targdate, datadir)
    assert 1==1


def test_createCameraFile():
    createCameraFile
    assert 1==1


def test_createWebpage():
    createWebpage(datadir)
    assert 1==1
