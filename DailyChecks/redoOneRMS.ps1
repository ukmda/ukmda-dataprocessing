# powershell script to rerun RMS-to-UFO conversion

#
# requires a Python 2.7 environment
# create this in Anaconda powershell: 
# conda create --name binviewer python=2.7
#
conda activate binviewer

# install prereqs just in case not already there

#conda install -y cython git gitpython
#conda install -y -c menpo opencv

# set env variable for cython - you'll need to tailor this
# to wherever your Visual C tools are

$env:VS90COMNTOOLS='C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools\'


$pwd = Get-Location
$targ = $args[0]
$src = $targ.substring($targ.lastindexof('UK'))

$ftpfil=$targ + '\FTPdetectinfo_' + $src +'.txt'    
$platepar = $targ + '\platepar_cmn2010.cal'

set-location 'C:\Users\mark\Documents\Projects\meteorhunting\RMS'
# create the CSV file
python -m Utils.RMS2UFO $ftpfil $platepar
# create the shower association map
python -m Utils.ShowerAssociation $ftpfil -x
# convert the FITS to jpegs
python -m Utils.BatchFFtoImage $targ jpg

#stack them if more than one to stack
$fits = $targ  + '\FF*.fits'
$nfits=(get-childitem $fits).count
if ($nfits -gt 1)
{
    python -m Utils.StackFFs $targ jpg -s  -x   
}
python -m Utils.GenerateMP4s $targ
set-location $pwd