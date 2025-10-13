# powershell script to get the 30 best detections from the previous night
# for sharing on social media
# note that you will have to go through and delete non-meteors from the images

# requirements - you must clone WesternMeteorPyLib and ukmda-dataprocessing from github
# to your local development space. I use onedrive\dev for my code - set this location in $codeloc


# copyright (c) Mark McIntyre, 2025-

set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
$bdir = $ini['localdata']['fbfolder'].replace('$HOME',$home)
$bdir = $bdir + "/brightest"
set-location $bdir

$outdir  = $bdir.replace('\','/')

$wmplloc = $ini['wmpl']['wmpl_loc'].replace('$HOME',$home)
$repdir = $ini['pylib']['pylib'].replace('$HOME',$home)

$env:pythonpath="$wmplloc"
Push-Location $repdir

conda activate ukmon-shared

Write-Output "working..."
if ($args.count -eq 0) {
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=30,outdir='$outdir')"
}else{
    $reqdate = $args[0]
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=30,outdir='$outdir', reqdate='$reqdate')"
}

$outdirw = $outdir.replace('/','\')
explorer "$outdirw"

Pop-Location