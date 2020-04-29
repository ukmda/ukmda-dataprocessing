# Script to create Shower maps
# start of main function

$pwd = get-location
Set-Location 'c:\users\mark\documents\projects\meteorhunting\RMS'
$ftpfil = $args[0]
if ($args.count -eq 1) 
{
    python -m Utils.ShowerAssociation $ftpfil
}else {
    python -m Utils.ShowerAssociation $ftpfil --config $args[1] #--hideplot    
}

set-location $pwd

