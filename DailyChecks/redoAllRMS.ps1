# powershell script to rerun RMS-to-UFO conversion

#
# requires a Python 2.7 environment
# create this in Anaconda powershell: 
# conda create --name binviewer python=2.7
#
# conda activate binviewer

# install prereqs just in case not already there

#conda install -y cython git gitpython
#conda install -y -c menpo opencv

# set env variable for cython - you'll need to tailor this
# to wherever your Visual C tools are

#$env:VS90COMNTOOLS='C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools\'


$pwd = Get-Location
$basedir='C:\Users\mark\Videos\astro\MeteorCam\UK0006\ConfirmedFiles'
$mindt = (get-date).AddDays(-14)
$dlist = (Get-ChildItem  -directory $basedir | Where-Object { $_.LastWriteTime -gt $mindt }).name
foreach ($src in $dlist)
{
    $targ = $basedir + '\' + $src
    $png=$targ+'\*.mp4'
    $ftp=$targ+'\FTPdetectinfo*.txt'

    $isdone=(get-childitem $png).Name
    $ftpexists=(get-childitem $ftp).name
    if ($isdone.count -eq 0 -and $ftpexists.count -ne 0){
        echo 'Processing' $targ
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
    }
    else
    {
        $msg= 'already processed ' + $src
        write-output $msg
    }
}
set-location $pwd