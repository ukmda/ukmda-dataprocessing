#!/bin/bash

conda activate wmpl

export PROJ4_VERSION=8.0.0
export PATH=/usr/local/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

# Compilation work for proj4
mkdir -p "/tmp/proj-${PROJ4_VERSION}-build"
pushd "/tmp/proj-${PROJ4_VERSION}-build"
curl -o "proj-${PROJ4_VERSION}.tar.gz" \
    "http://download.osgeo.org/proj/proj-${PROJ4_VERSION}.tar.gz" \
    && tar xfz "proj-${PROJ4_VERSION}.tar.gz"
rm -f proj-${PROJ4_VERSION}.tar.gz

cd "/tmp/proj-${PROJ4_VERSION}-build/proj-${PROJ4_VERSION}"
./configure --prefix=/usr/local/proj4

# Make in parallel with 2x the number of processors.
make -j $(( 2 * $(cat /proc/cpuinfo | egrep ^processor | wc -l) )) \
 && sudo make install \
 && sudo ldconfig

