# Copyright (C) 2018-2023 Mark McIntyre
FROM continuumio/miniconda3

RUN conda install -y -c conda-forge numpy scipy matplotlib cython pytz pyqt
RUN conda install -y -c conda-forge jplephem ephem
RUN conda install -y -c conda-forge basemap basemap-data-hires
RUN conda install -y -c conda-forge pandas cartopy

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./
RUN pip install boto3
COPY *.py ./

COPY awskeys ./

ENTRYPOINT ["python", "trajsolver.py"]
