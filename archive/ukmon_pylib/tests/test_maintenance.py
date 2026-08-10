# simple test for fix to bug 493

import os
from maintenance.recreateOrbitPages import recreateOrbitFiles
from zipfile import ZipFile

here = os.path.split(os.path.abspath(__file__))[0]
datadir = os.getenv('TMP', default='/tmp')

with ZipFile(os.path.join(here,'test_maint.zip'),'r') as zip_ref:
    zip_ref.extractall(here)

def test_recreateOrbitPages():
    outdir = '20260721_214634/20260721_214634.406_UK'
    pickfile = [x for x in os.listdir(outdir) if '.pickle' in x][0]
    recreateOrbitFiles(outdir, pickfile, False)
    assert 1==1