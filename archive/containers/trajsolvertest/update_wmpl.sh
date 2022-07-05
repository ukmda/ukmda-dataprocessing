#!/bin/bash
cd /mnt/e/dev/meteorhunting/ukmon-shared/archive/containers/trajsolver/
rsync -avz ukmonhelper:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "__pycache__/"
rm -Rf ./WesternMeteorPyLib/wmpl/MetSim
rm -Rf ./WesternMeteorPyLib/wmpl/CAMO
cd ./WesternMeteorPyLib/wmpl/Utils/
mv ./DynamicMassFit.py  ./DynamicMassFit.notused
# temporary hack till i get cartopy working
mv ./PlotMap_OSM.py ./PlotMap_OSM.py.notused