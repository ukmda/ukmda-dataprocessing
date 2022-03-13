#!/bin/bash

export CARTOPY_VERSION=0.19.0

mkdir -p "/tmp/cartopy-${CARTOPY_VERSION}-build"
pushd "/tmp/cartopy-${CARTOPY_VERSION}-build"
git clone https://github.com/SciTools/cartopy.git
cd cartopy
git fetch
git switch --detach tags/v${CARTOPY_VERSION}
export CPATH=/usr/local/proj4/include
export PATH=$PATH:/usr/local/proj4/bin:/usr/local/geos/bin
export LIBRARY_PATH=/usr/local/proj4/lib:/usr/local/geos/lib
python setup.py install


