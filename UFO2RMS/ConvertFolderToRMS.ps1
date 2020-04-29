# convert whole directory to RMS format

# start of main function
$pwd = get-location

$fils=get-childitem -path '*A.xml' -recurse
$nfils=$fils.count
if($nfils -gt 1){
    $fn1=$fils[0].Name
}else{
    $fn1=$fils.Name
}
$ymd=$fn1.substring(1,8)
$tail=$fn1.substring(17)
$cam=$tail.substring(0,$tail.length-5)
$lid=$cam.substring(0,$cam.indexof('_'))
$sid=$cam.substring($cam.indexof('_')+1)

$ofname = [string]$pwd+'\FTPdetectinfo_'+$lid+$sid+'_'+$ymd+'_000000_0000000.txt'
'Meteor Count = '+$nfils | out-file -path $ofname 
'-----------------------------------------------------'| out-file -path $ofname -Append
'Processed with powershell scripts by MJMM' | out-file -path $ofname -Append
'-----------------------------------------------------'| out-file -path $ofname -Append
'FF  folder = '+[string]$pwd | out-file -path $ofname -Append
'CAL folder = /nowhere' | out-file -path $ofname -Append
'-----------------------------------------------------'| out-file -path $ofname -Append
'FF  file processed'| out-file -path $ofname -Append
'CAL file processed'| out-file -path $ofname -Append
'Cam# Meteor# #Segments fps hnr mle bin Pix/fm Rho Phi'| out-file -path $ofname -Append
'Per segment:  Frame# Col Row RA Dec Azim Elev Inten Mag'| out-file -path $ofname -Append

get-childitem -path '*A.xml' -Recurse | foreach-object -Process {
    $thisfile=$_.fullname
    $msg='processing '+$thisfile
    write-output $msg
    & $PSScriptRoot\ConvertToRMS.ps1 $thisfile $ofname
}
& $PSScriptRoot\CreateMaps.ps1 $ofname .config.inuse
set-location $pwd

