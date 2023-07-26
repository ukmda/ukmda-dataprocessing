#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

targ=trajsolver

cd /mnt/e/dev/meteorhunting/ukmon-shared/archive/containers/$targ/
ssh ukmonhelper2 "cd src/wmpldev && git stash && git checkout forcontainer && git pull"
rsync -avz ukmonhelper2:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "__pycache__/"
ssh ukmonhelper2 "cd src/wmpldev && git checkout - && git stash apply"

# remove  modules and code that don't work in a container because theres no GUI
rm -Rf ./WesternMeteorPyLib/wmpl/MetSim
rm -Rf ./WesternMeteorPyLib/wmpl/CAMO
rm -f  ./WesternMeteorPyLib/wmpl/Utils/DynamicMassFit.py
