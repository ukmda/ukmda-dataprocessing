#!/bin/bash

#install the versions of GEOS, SQLITE3, PROJ4 that are required for cartopy 0.20 or later

export SQLVER=3390000
export PROJ4_VERSION=8.0.0
export GEOS_VERSION=3.7.2

mkdir -p /tmp/sqlite3
pushd /tmp/sqlite3
wget http://www.sqlite.org/2022/sqlite-autoconf-${SQLVER}.tar.gz
tar xvzf sqlite-autoconf-${SQLVER}.tar.gz
rm -Rf sqlite-autoconf-${SQLVER}.tar.gz
cd sqlite-autoconf-${SQLVER}/
./configure
make -j $(( 2 * $(cat /proc/cpuinfo | egrep ^processor | wc -l) )) && make install
if [ $? -ne 0 ] ; then exit 1 ; fi
popd 
rm -Rf /tmp/sqlite3

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

make -j $(( 2 * $(cat /proc/cpuinfo | egrep ^processor | wc -l) )) \
 && make install # && ldconfig
if [ $? -ne 0 ] ; then exit 1 ; fi
popd
rm -Rf "/tmp/proj-${PROJ4_VERSION}-build"

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
 && make install # && ldconfig
if [ $? -ne 0 ] ; then exit 1 ; fi
popd
rm -Rf "/tmp/geos-${GEOS_VERSION}-build"
