# convert whole day's worth of data to RMS format
param(
    [string]$inf="nope"
)
#process one record from an A.XML file
function processonerecord($rec, $ofname)
{
    #process a single meteor record from a UA file
    $nseg = $rec.ua2_objpath.ua2_fdata2.count
    for ($j=0; $j -lt $nseg ; $j++)
    {
        $seg=$rec.ua2_objpath.ua2_fdata2[$j]

        #Per segment:  Frame# Col Row RA Dec Azim Elev Inten Mag
        $ostr= $seg.fno+' 0.0 0.0 '+$seg.ra+' '+$seg.dec+' '+$seg.az+' '+$seg.ev+' '+$seg.b+' '+$seg.mag
        $ostr | out-file -path $ofname -append
    }
}
# read an A.XML file and process it
function readUAxml($fname, $on)
{
    # read a UFO Analyser XML file and extract the meteor track data
    $srcpath=$fname | split-path
    [xml]$f=get-content $fname # read the XML file

    #get the station details and time+date
    $lid=$f.ufoanalyzer_record.lid
    $sid=$f.ufoanalyzer_record.sid
    $fps=[double]($f.ufoanalyzer_record.fps)
    $yr=$f.ufoanalyzer_record.y
    $mo=($f.ufoanalyzer_record.mo).tostring().padleft(2,'0')
    $dy=($f.ufoanalyzer_record.d).tostring().padleft(2,'0')
    $hr=($f.ufoanalyzer_record.h).tostring().padleft(2,'0')
    $mi=($f.ufoanalyzer_record.m).tostring().padleft(2,'0')
    $se=$f.ufoanalyzer_record.s
    $s = [math]::floor($se)
    $ms=[int](($se-$s)*1000)
    $ss=$s.tostring().padleft(2,'0')
    $mss=$ms.tostring().padleft(3,'0')
    $fpss=("{0:n2}" -f [double]$fps).tostring().padleft(7,'0')
    $pixfm='001.5'
    $rho='0000.0'
    $phi='0000.0'
    if($on -eq 'nope')
    {
        $ofname = $srcpath+'\FTPdetectinfo_'+$lid+$sid+'_'+$yr+$mo+$dy+'_000000_0000000.txt'
    }
    else 
    {
        $ofname = $on
    }
    $recs = $f.ufoanalyzer_record.ua2_objects
    if ($recs.count -eq 1)
    {
        $rec = $recs.ua2_object
        $nseg = $rec.ua2_objpath.ua2_fdata2.count
        if ($nseg -gt 1)
        {
            '-------------------------------------------------------' | out-file $ofname -append
            $l1='FF_'+$lid+$sid+'_'+$yr+$mo+$dy+'_'+$hr+$mi+$ss+'_'+$mss+'_0000000.JPG'
            $l1 | out-file -path $ofname -append 
            'Recalibrated with UFOAnalyser on:' + (get-date -uformat('%Y-%m-%d %H:%M:%S'))| out-file -path $ofname -Append
            #UK0006 0001 0015 0025.00 000.0 000.0  00.0 017.0 0301.1 0093.2
            $lid+$sid+' 0001 '+$nseg+' '+$fpss+' 000.0 000.0  00.0 '+$pixfm+' '+$rho+' '+$phi | out-file -path $ofname -Append
            processonerecord $rec $ofname
        }
    }
    else
    {
        for ($i=0;$i -lt $recs.count ; $i++ )
        {
            $rec = $recs.ua2_object[$i]
            $nseg = $rec.ua2_objpath.ua2_fdata2.count
            if($nseg -gt 1) 
            {
                '-------------------------------------------------------' | out-file $ofname -append
                $l1='FF_'+$lid+$sid+'_'+$yr+$mo+$dy+'_'+$hr+$mi+$ss+'_'+$mss+'_0000000.JPG'
                $l1 | out-file -path $ofname -append 
                'Recalibrated with UFOAnalyser on:' + (get-date -uformat('%Y-%m-%d %H:%M:%S'))| out-file -path $ofname -Append
                #UK0006 0001 0015 0025.00 000.0 000.0  00.0 017.0 0301.1 0093.2
                $lid+$sid+' 0001 '+$nseg+' '+$fpss+' 000.0 000.0  00.0 '+$pixfm+' '+$rho+' '+$phi | out-file -path $ofname -Append
                processonerecord $rec $ofname
            }
        }
    }
}

if ($inf  -eq "nope")
{
    write-output "Usage: UFO2RMS.ps1 srcpath"
}
else
{
    $pwd = get-location
    $srcpth=$inf+'\*A.xml'
    $fils=get-childitem -path $srcpth -recurse
    $nfils=$fils.count
    if($nfils -gt 1)
    {
        $fn1=$fils[0].Name
    }
    else
    {
        $fn1=$fils.Name
    }
    $ymd=$fn1.substring(1,8)
    $tail=$fn1.substring(17)
    $cam=$tail.substring(0,$tail.length-5)
    $lid=$cam.substring(0,$cam.indexof('_'))
    $sid=$cam.substring($cam.indexof('_')+1)

    $ofname = [string]$inf+'\FTPdetectinfo_'+$lid+$sid+'_'+$ymd+'_000000_0000000.txt'
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

    get-childitem -path $srcpth -Recurse | foreach-object -Process {
        $thisfile=$_.fullname
        $fn=$_.Name
        write-output "processing $fn"
        readUAxml $thisfile $ofname
    }
    write-output "wrote to $ofname"
    get-content $ofname
    set-location $pwd
}
