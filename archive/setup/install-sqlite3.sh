#!/bin/bash
cd /tmp
mkdir sqlite3
cd sqlite3
export SQLVER=3390000
wget http://www.sqlite.org/2022/sqlite-autoconf-${SQLVER}.tar.gz
tar xvzf sqlite-autoconf-${SQLVER}.tar.gz
cd sqlite-autoconf-${SQLVER}/
./configure
make && sudo make install

