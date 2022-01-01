#
# manually reduce one camera folder 
#

# args : arg1 date, arg2 stationid
$loc = Get-Location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
set-location $fbfldr

# read date and camera ID from commandline
$dt = [string]$args[0]
$cam = $args[1]

# create target path
$tf = $cam + '_' + $dt + '_180000'
$targpth = "$fbfldr\$dt\$cam\$tf"

# run SkyFit to refine the platepar and reduce the path
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH=$ini['rms']['rms_loc']
push-Location $ini['rms']['rms_loc']
python -m Utils.SkyFit2 $targpth -c $targpth\.config
python -m Utils.BatchFFtoImage $targpth jpg
$ftpname=(Get-ChildItem $targpth\FTP*manual.txt).name
python -m Utils.RMS2UFO $ftpname $targpth\platepar_cmn2010.cal

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

