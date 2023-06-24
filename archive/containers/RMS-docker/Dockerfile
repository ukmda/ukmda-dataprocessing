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
   unzip ffmpeg imagemagick mplayer unzip less nano curl \
   iputils-ping dnsutils

# setup sshd for remote access
RUN mkdir -p /run/sshd
RUN echo 'root:ubuntu' | chpasswd
RUN ssh-keygen -A
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
EXPOSE 22

WORKDIR /root/source
RUN git clone https://github.com/CroatianMeteorNetwork/RMS.git
WORKDIR /root/source/RMS
RUN pip3 install -r requirements.txt
#RUN python3 setup.py install

RUN ln -s /usr/bin/python3 /usr/local/bin/python

ENV DOCKER_RUNNING true 
CMD ["/root/RMS_data/config/configure_container.sh"]
