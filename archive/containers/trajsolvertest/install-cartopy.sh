#!/bin/bash

export CARTOPY_VERSION=0.20.3

export PATH=/usr/local/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

pip install Cython numpy shapely pyshp pyproj matplotlib pillow scipy

mkdir -p "/tmp/cartopy-${CARTOPY_VERSION}-build"
pushd "/tmp/cartopy-${CARTOPY_VERSION}-build"
git clone https://github.com/SciTools/cartopy.git
cd cartopy
git fetch
git switch --detach tags/v${CARTOPY_VERSION}
export CPATH=/usr/local/proj4/include
export PATH=usr/local/proj4/bin:/usr/local/geos/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/proj4/lib:/usr/local/geos/lib
if [ ! -f lib/cartopy/_version.py ] ; then 
    echo "version='0.20.3'" > lib/cartopy/_version.py
    echo "version_tuple = (0, 19, 0)" >> lib/cartopy/_version.py
fi
python setup.py build_ext -I /usr/local/proj4/include -I /usr/local/geos/include 
python setup.py install
if [ $? -ne 0 ] ; then exit 1 ; fi
popd
rm -Rf "/tmp/cartopy-${CARTOPY_VERSION}-build"
