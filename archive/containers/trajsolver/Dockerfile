# Copyright (C) 2018-2023 Mark McIntyre
FROM continuumio/miniconda3:4.11.0

RUN conda install -y -c conda-forge "numpy<1.25.0" scipy cython pytz pyqt
RUN conda install -y -c conda-forge jplephem ephem
RUN conda install -y -c conda-forge basemap basemap-data-hires
RUN conda install -y -c conda-forge pandas cartopy
RUN conda install -y matplotlib=3.4.3 
RUN pip install boto3
RUN apt-get update && apt-get -y upgrade 
RUN conda install -y -c conda-forge numba

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./
COPY *.py ./
#ENV NUMPY_EXPERIMENTAL_DTYPE_API 1

COPY awskey[s] ./

ENTRYPOINT ["python", "trajsolver.py"]
