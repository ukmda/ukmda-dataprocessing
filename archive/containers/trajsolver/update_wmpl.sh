#!/bin/bash
cd /mnt/e/dev/meteorhunting/ukmon-shared/archive/containers/trajsolver/
rsync -avz ukmonhelper:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "__pycache__/"
rm -Rf ./WesternMeteorPyLib/wmpl/MetSim
rm -Rf ./WesternMeteorPyLib/wmpl/CAMO