sudo apt install dirmngr ca-certificates software-properties-common apt-transport-https -y
sudo gpg --list-keys
echo 'deb [signed-by=/usr/share/keyrings/deadsnakes.gpg] https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main' | sudo tee -a /etc/apt/sources.list.d/python.list
sudo apt update

sudo apt install python3.8 -y
