#!/bin/bash

# copyright Mark McIntyre, 2026-

# Script to update WMPL on the server

[ "$RUNTIME_ENV" == "PROD" ] && targdir=$HOME/src/WesternMeteorPyLib || targdir=$HOME/src/wmpldev

pushd $targdir
git fetch 
git pull

[ -d wmpl/MetSim ] && rm -Rf wmpl/MetSim
[ -d wmpl/CAMO ] && rm -Rf wmpl/CAMO
[ -f wmpl/Utils/DynamicMassFit.py ] && rm -f wmpl/Utils/DynamicMassFit.py

python << EOD
from UpdateOrbitFiles import updateOrbitFiles
from wmpl.Utils.ShowerAssociation import loadGMNShowerTable
import urllib.request as urllibrary
import os
de430_file_path = os.path.join('wmpl', 'share', 'de430.bsp')
if not os.path.isfile(de430_file_path):
 de430_url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp"
 urllibrary.urlretrieve(de430_url, de430_file_path)

updateOrbitFiles()

EOD
popd

echo "make sure you have updated the containers:"
echo "  trajsolver"
echo ""
echo "And the lambdas:"
echo "  getExtraFilesV2"
echo "  matchpickle"
