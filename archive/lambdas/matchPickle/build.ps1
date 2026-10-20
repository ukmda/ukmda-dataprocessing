# build script for the docker image
# Copyright (C) 2018-2023 Mark McIntyre

$loc = get-location
set-location $psscriptroot

$yn=read-host -prompt "update WMPL?"
if ($yn.tolower() -eq "y")
{
    pushd pythoncode
    ssh ukmbatch "cd ~/src/wmpldev && git stash && git checkout distrib_processing && git pull"
    ssh ukmbatch "cd ~/src/wmpldev && find . -type d -name __pycache__ -exec rm -Rf {} \;"
    bash -c 'rsync -avz ukmbatch:src/wmpldev/* ./WesternMeteorPyLib/ --exclude "build/" --exclude "*.egg*" --exclude "dist/" --exclude ".git/" --exclude "**/*.bsp"  --exclude "wmpl/MetSim" --exclude "wmpl/CAMO" '
    pushd WesternMeteorPyLib
    if (test-path wmpl/MetSim) {Remove-Item -Recurse wmpl/MetSim}
    if (test-path wmpl/CAMO) {Remove-Item -Recurse wmpl/CAMO}
    if (test-path wmpl/Utils/DynamicMassFit.py) {Remove-Item wmpl/Utils/DynamicMassFit.py}
    if (test-path wmpl/Utils/DynamicMassFit.py) {Remove-Item wmpl/Utils/DynamicMassFit.py}
    bash -c "rsync -avz ../../../../../../wmpl_master/wmpl/Utils/Orbit* ./wmpl/Utils"
    conda activate wmpl
    python ./UpdateOrbitFiles.py
    echo "getting DE430 Planetary Ephemerides Kernel"
    curl "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp" -o wmpl/share/de430.bsp
    python -c "from wmpl.Utils.ShowerAssociation import loadGMNShowerTable"
    conda deactivate
    popd
    popd
}

sam build

set-location $loc
