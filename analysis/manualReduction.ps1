#
# manually reduce one camera folder 
#
# args : arg1 date, arg2 stationid

if ($args.count -lt 2) {
    write-output "usage: manualReduction.ps1 yyyymmdd UKxxxxx"
    exit 1
}

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

#$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
set-location $fbfldr

# read date and camera ID from commandline
$dt = [string]$args[0]
$cam = $args[1]

# locate target path
$tf = $cam + '_' + $dt + '_*'
$targpth = "$fbfldr\$dt\$cam\$tf"
$targpth = (Get-ChildItem $targpth).fullname
if (!$targpth) { $targpth = "$fbfldr\$dt\$cam" }
if ((test-path $targpth) -eq 0) { 
    $targpth = "$fbfldr\$dt*\$dt*\$cam" 
    $targpth = (Get-ChildItem $targpth).fullname
}

if ((test-path $targpth\.config) -eq 0) {
    write-output "no config file so can't continue"
    pop-location
    exit 1
}

write-output "processing $targpth"

# run SkyFit to refine the platepar and reduce the path
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH=$ini['rms']['rms_loc']
push-Location $ini['rms']['rms_loc']
python -m Utils.BatchFFtoImage $targpth jpg
python -m Utils.SkyFit2 $targpth -c $targpth\.config
$ftpname=(Get-ChildItem $targpth\FTP*manual.txt).name
python -m Utils.RMS2UFO $targpth\$ftpname $targpth\platepar_cmn2010.cal

$ffname=(Get-ChildItem $targpth\FF*.fits).name
if ($ffname -is [array])
{
    write-output '{' > $targpth/platepars_all_recalibrated.json
    for ($i=0;$i -lt $ffname.Length ; $i++)
    {
        copy-item $targpth\$ffname[$i] $targpth\upload 
        $hdr='"' + $ffname[$i] + '": '
        Write-Output $hdr >> $targpth/platepars_all_recalibrated.json
        (Get-Content -path $targpth/platepar_cmn2010.cal -Raw) -replace '"auto_recalibrated": false','"auto_recalibrated": true' >> $targpth/platepars_all_recalibrated.json
        if ($i -lt $ffname.length-1) {write-output ',' >> $targpth/platepars_all_recalibrated.json}
    }
    Write-Output "}" >> $targpth/platepars_all_recalibrated.json
}
else {
    $hdr='{"'+$ffname+'": '
    Write-Output $hdr > $targpth/platepars_all_recalibrated.json
    (Get-Content -path $targpth/platepar_cmn2010.cal -Raw) -replace '"auto_recalibrated": false','"auto_recalibrated": true' >> $targpth/platepars_all_recalibrated.json
    Write-Output "}" >> $targpth/platepars_all_recalibrated.json
}
pop-location

