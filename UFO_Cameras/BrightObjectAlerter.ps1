# script to detect bright objects and warn me 
# 

#set up the location to work in
Import-Module PowerShell-SMS
$key = (get-storedcredential -target Nexmo).UserName
$pass = (get-storedcredential -target Nexmo).GetNetworkCredential().Password
set-nexmo -apikey $key -APISecret $pass
$phoneno='+447581483115'

$caploc=(get-content $env:userprofile"\appdata\local\ukmonlivewatcher.ini")[1]
$logf= $caploc+"brightobjs.log"
if((test-path $logf) -eq $false)
{
    new-item -path $logf
}
$camname=$args[0]
$basedir=$caploc

if ($args.Count -lt 1)
{
    write-output "usage : BrightObjectAlerter {cameraSID}"
}
else {
    if($args.count -eq 2)
    {
        $yyyy=([string]$args[1]).substring(0,4)
        $mm = ([string]$args[1]).substring(0,6)
        $dd= ([string]$args[1]).substring(0,8)
    }else 
    {
        $yyyy = get-date -format "yyyy"
        $mm = [string](get-date -format "yyyyMM")
        $dd= [string](get-date -format "yyyyMMdd")
    }

    $targ=$basedir+'\'+$yyyy+'\'+$mm+'\'+$dd+'\M*'+$camname+'.xml'
    $flist = (get-childitem $targ).fullname
    $fns = (get-childitem $targ).name
    if ($flist.count -eq 0) {write-output "No files found"}

    for ($i=0 ; $i -lt $flist.count; $i++)
    {
        if ($flist.count -gt 1) {
            $infile=$flist[$i]
            $fn = $fns[$i]
        }else {
            $infile=$flist
            $fn = $fns
        }
        # read the file and cast it to an XML doc
        [xml]$rawfile=get-content -path $infile
        $maxbright=($rawfile.ufocapture_record.ufocapture_paths.uc_path.bmax | measure-object -maximum).maximum
        if ($maxbright -gt 200){
            if((get-childitem $logf | select-string $fn).length -eq 0){
                add-content $logf $fn
                $msg = "Possible interesting event " + $fn
                write-output $msg
                send-sms -to $phoneno -from $phoneno $msg -provider Nexmo
            } 
        }else {
            write-output '.'
        }
    }
}