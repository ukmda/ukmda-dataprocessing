# powershell script to get the 30 best detections from the previous night
# for sharing on social media
# note that you will have to go through and delete non-meteors from the images

# requirements - you must clone WesternMeteorPyLib and ukmda-dataprocessing from github
# to your local development space. I use onedrive\dev for my code - set this location in $codeloc

# you also need to specify the output folder, $outdir

# copyright (c) Mark McIntyre, 2025-

$codeloc ="$env:userprofile\onedrive\dev" 
$outdirw = "$env:userprofile\pictures\_ToBeProcessed\brightest"

$repdir = "$codeloc\ukmda-dataprocessing\archive\ukmon_pylib"
$outdir  = $outdirw.replace('\','/')

$env:pythonpath="$codeloc\WesternMeteorPyLib"
Push-Location $repdir

conda activate ukmon-shared

Write-Output "working..."
if ($args.count -eq 0) {
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=30,outdir='$outdir')"
}else{
    $reqdate = $args[0]
    python -c "from reports.findBestMp4s import getBestNSingles;getBestNSingles(numtoget=30,outdir='$outdir', reqdate='$reqdate')"
}

explorer "$outdirw"

Pop-Location