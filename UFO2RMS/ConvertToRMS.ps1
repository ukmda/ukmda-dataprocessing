# Script to create Shower maps
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
function readUAxml($fname, $srcpath, $on)
{
    # read a UFO Analyser XML file and extract the meteor track data
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
# start of main function
$pwd = get-location
$srcpath=[string]$pwd
Set-Location 'c:\users\mark\documents\projects\meteorhunting\RMS'
$inf = $args[0]
$on = 'nope'
if($args.count -gt 1) {$on = $args[1]}
$xmlfil= (get-childitem -path $inf).fullname

readUAxml $xmlfil $srcpath $on

set-location $pwd

