#!/bin/bash

conda activate wmpl

export PROJ4_VERSION=4.9.3

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

popd

export GEOS_VERSION=3.7.2

# Compilation work for geos
mkdir -p "/tmp/geos-${GEOS_VERSION}-build"
pushd "/tmp/geos-${GEOS_VERSION}-build"
curl -o "geos-${GEOS_VERSION}.tar.bz2" \
    "http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2" \
    && bunzip2 "geos-${GEOS_VERSION}.tar.bz2" \
    && tar xvf "geos-${GEOS_VERSION}.tar"
rm -f geos-${GEOS_VERSION}.tar.bz2

cd "/tmp/geos-${GEOS_VERSION}-build/geos-${GEOS_VERSION}"
./configure --prefix=/usr/local/geos

# Make in parallel with 2x the number of processors.
make -j $(( 2 * $(cat /proc/cpuinfo | egrep ^processor | wc -l) )) \
 && sudo make install \
 && sudo ldconfig

popd
