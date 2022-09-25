#!/bin/bash
cd /mnt/e/dev/meteorhunting/ukmon-shared/archive/containers/trajsolver/
ssh ukmonhelper "cd src/wmpldev && git stash && git checkout forcontainer && git pull"
rsync -avz ukmonhelper:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "__pycache__/"
ssh ukmonhelper "cd src/wmpldev && git checkout - && git stash apply"
# remove or rename modules and code that don't work in a container
rm -Rf ./WesternMeteorPyLib/wmpl/MetSim
rm -Rf ./WesternMeteorPyLib/wmpl/CAMO
cd ./WesternMeteorPyLib/wmpl/Utils/
# references a module that requires the GUI, which isn't present in a container
mv ./DynamicMassFit.py  ./DynamicMassFit.py.notused
# temporary hack till i get cartopy working
mv ./PlotMap_OSM.py ./PlotMap_OSM.py.notused
