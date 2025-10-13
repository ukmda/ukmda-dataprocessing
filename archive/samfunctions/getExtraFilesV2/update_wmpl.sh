#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $here/pythoncode
ssh ukmonhelper2 "cd src/wmpldev && git stash && git checkout forcontainer && git pull"
rsync -avz ukmonhelper2:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "__pycache__/"
ssh ukmonhelper2 "cd src/wmpldev && git checkout - && git stash apply"

mv -f ./WesternMeteorPyLib/wmpl/Trajectory/lib/trajectory/libtrajectorysolution.so.0 ./WesternMeteorPyLib/wmpl/Trajectory/lib/trajectory/libtrajectorysolution.so
# remove  modules and code that don't work in a container because theres no GUI
rm -Rf ./WesternMeteorPyLib/wmpl/MetSim
rm -Rf ./WesternMeteorPyLib/wmpl/CAMO
rm -f  ./WesternMeteorPyLib/wmpl/Utils/DynamicMassFit.py
rm -f  ./WesternMeteorPyLib/wmpl/Utils/PlotMap_OSM.py
cp ./wmpl__init__.py_fixed.py ./WesternMeteorPyLib/wmpl/__init__.py
