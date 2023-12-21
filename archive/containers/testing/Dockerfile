# Copyright (C) 2018-2023 Mark McIntyre
FROM continuumio/miniconda3:4.11.0
RUN conda install -y -c conda-forge "numpy<1.25.0" scipy cython pytz pyqt
RUN conda install -y -c conda-forge jplephem ephem
RUN conda install -y -c conda-forge basemap basemap-data-hires
RUN conda install -y -c conda-forge pandas cartopy
RUN conda install -y matplotlib=3.4.3 
RUN pip install boto3
RUN apt update
RUN apt -y upgrade 
RUN apt install -y apt-utils
RUN apt install -y curl
RUN apt install -y iputils-ping
COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
COPY RMS/ ./RMS
ENV PYTHONPATH ./WesternMeteorPyLib:./RMS
ENV PROJ_LIB ./
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install
RUN pip install MeteorTools
ADD https://archive.ukmeteors.co.uk/browse/testdata/testdata.tar.gz ./data/ 
RUN cd ./data && tar -xzf ./testdata.tar.gz
COPY *.py ./
COPY tests.sh ./
CMD [ "bash" , "./tests.sh"]