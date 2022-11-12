#!/bin/bash

export CARTOPY_VERSION=0.20.3

mkdir -p "/tmp/cartopy-${CARTOPY_VERSION}-build"
pushd "/tmp/cartopy-${CARTOPY_VERSION}-build"
git clone https://github.com/SciTools/cartopy.git
cd cartopy
git fetch
git switch --detach tags/v${CARTOPY_VERSION}
export CPATH=/usr/local/proj4/include
export PATH=usr/local/proj4/bin:/usr/local/geos/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/proj4/lib:/usr/local/geos/lib
python setup.py build_ext -I /usr/local/proj4/include -I /usr/local/geos/include 
python setup.py install


