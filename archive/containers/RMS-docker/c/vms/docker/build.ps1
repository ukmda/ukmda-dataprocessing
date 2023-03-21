# build the container

# path\to\rmsdata must exist and must contain a folder "config"
# containing the platepar, mask, RMS config file, id_rsa and id_rsa.pub files. 
if ($args.count -lt 1) {
    write-output "usage: .\login.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]

copy-item configure_container.sh $configloc\config
docker build . -t rms_ubuntu