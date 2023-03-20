FROM scratch
LABEL version=0.1
#FROM dorowu/ubuntu-desktop-lxde-vnc
FROM ubuntu:20.04
RUN apt-get update
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install -y ssh net-tools vim-gui-common vim-runtime cron

RUN apt-get install -y python3.8 python3-pip git \
   python3.8-tk libxslt-dev python-imaging-tk \
   gnome-session-wayland libopencv-dev python3-opencv \
   unzip ffmpeg imagemagick mplayer unzip less nano 
WORKDIR /root/source
RUN git clone https://github.com/CroatianMeteorNetwork/RMS.git
WORKDIR /root/source/RMS
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

RUN apt-get install -y iputils-ping dnsutils
RUN ln -s /usr/bin/python3 /usr/local/bin/python

WORKDIR /root/source
RUN git clone https://github.com/markmac99/ukmon-pitools.git
WORKDIR /root/source/RMS

ENV DOCKER_RUNNING true 
CMD ["/root/RMS_data/config/configure_container.sh"]
