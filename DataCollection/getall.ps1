set-location $PSScriptRoot
$now=(get-date -uformat '%Y%m%d')
$logf="..\logs\"+$now+".log"
Write-Output "starting to get all data" > $logf
.\getDataFromCamera.ps1 .\tackley_ne.ini >> $logf
.\getDataFromCamera.ps1 .\tackley_tc.ini >> $logf
.\getDataFromCamera.ps1 .\UK0006.ini >> $logf
.\getDataFromCamera.ps1 .\UK000F.ini >> $logf
.\getDataFromRadio.ps1 >> $logf
Write-Output "got all data" >> $logf

set-location $PSScriptRoot
if((test-path .\dayornight.txt) -eq - $false)
{
    $curdn=(.\sunwait.exe poll +51.88N +1.31W)    
    Write-Output $curdn > .\dayornight.txt
}
$lastdn=get-content .\dayornight.txt
$curdn=(.\sunwait.exe poll +51.88N +1.31W)
#if ($curdn -ne $lastdn -and $curdn -eq "DAY"){
    write-output "curating UFO cameras" >> $logf
    Write-Output $curdn > .\dayornight.txt
    conda activate RMS

    python -V > c:\temp\foo.log

    $dt=get-date -uformat '%Y%m%d'
    write-output "processing $dt TC" >> $logf
    & python .\curateCamera.py .\tackley_tc.ini $dt >> $logf
    write-output "processing $dt NE" >> $logf
    & python .\curateCamera.py .\tackley_ne.ini $dt >> $logf

    $dt=(get-date).adddays(-1).tostring('yyyyMMdd')
    write-output "processing $dt" >> $logf

    write-output "processing $dt TC" >> $logf
    $res = python .\curateCamera.py .\tackley_tc.ini $dt
    $res >> $logf
    write-output $res >> $logf
    write-output "processing $dt NE" >> $logf
    $res = python .\curateCamera.py .\tackley_ne.ini $dt
    write-output $res >> $logf

    write-output "done" >> $logf
#}
set-location $PSScriptRoot
if ((get-date).hour -eq 20 ) {
    write-output "refreshing website" >> $logf
    .\pushtowebsite.ps1
}

set-location $PSScriptRoot
if ((get-date).hour -eq 8 ) {
    write-output "refreshing UKMON archive" >> $logf
    .\ukmon-archive\get-archive.ps1
}

$dt= (get-date -uformat '%Y-%m-%d %H:%M:%S')
write-output "getall finished at $dt"
