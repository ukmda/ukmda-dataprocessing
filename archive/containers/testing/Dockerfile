# Copyright (C) 2018-2023 Mark McIntyre
FROM continuumio/miniconda3:4.11.0
RUN conda install -y -c conda-forge "numpy<1.25.0" scipy cython pytz pyqt
RUN conda install -y -c conda-forge jplephem ephem
RUN conda install -y -c conda-forge basemap basemap-data-hires
RUN conda install -y -c conda-forge pandas cartopy
RUN conda install -y matplotlib=3.4.3 
RUN pip install boto3
RUN apt-get update && apt-get -y upgrade 

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
COPY RMS/ ./RMS
ENV PYTHONPATH ./WesternMeteorPyLib:./RMS
ENV PROJ_LIB ./
COPY *.py ./
COPY tests.sh ./

ENTRYPOINT [ "bash" , "./tests.sh"]