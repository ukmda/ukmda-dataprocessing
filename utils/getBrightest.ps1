# powershell script to get the 30 best detections from the previous night
# for sharing on social media
# note that you will have to go through and delete non-meteors from the images

# requirements - you must clone WesternMeteorPyLib and ukmda-dataprocessing from github
# to your local development space. I use onedrive\dev for my code - set this location in $codeloc


# copyright (c) Mark McIntyre, 2025-

Param($config='analysis.ini', $reqdate='', $todate='')

# load the helper functions
. $PSScriptRoot\helperfunctions.ps1

$ini=get-inicontent "$psscriptroot\$config"

$bdir = $ini['localdata']['fbfolder'].replace('$HOME',$home)
$bdir = $bdir + "/brightest"

$outdir  = $bdir.replace('\','/')

$wmplloc = $ini['wmpl']['wmpl_loc'].replace('$HOME',$home)
$repdir = $ini['pylib']['pylib'].replace('$HOME',$home)

$env:pythonpath="$wmplloc"
Push-Location $repdir

conda activate ukmon-shared

if ($todate -eq "") { $todate = $reqdate}

if ($reqdate -eq "" ) {
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=30,outdir='$outdir')"
}else{
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=50,outdir='$outdir', reqdate='$reqdate', todate='$todate')"
}

$outdirw = $outdir.replace('/','\')
explorer "$outdirw"

Pop-Location