# Copyright (C) 2018-2023 Mark McIntyre
FROM anaconda/miniconda:latest

ENV CONDA_PLUGINS_AUTO_ACCEPT_TOS=true
RUN conda create -n wmpl python=3.11 && conda config --set default_activation_env wmpl

RUN conda install -n wmpl -y -c conda-forge "numpy<2" scipy cython pytz pyqt
RUN conda install -n wmpl -y -c conda-forge jplephem ephem
RUN conda install -n wmpl -y -c conda-forge basemap basemap-data-hires
RUN conda install -n wmpl -y -c conda-forge pandas cartopy
RUN conda install -n wmpl -y matplotlib
RUN . /opt/miniconda3/etc/profile.d/conda.sh && conda activate wmpl && pip install boto3
RUN apt-get update && apt-get -y upgrade 
RUN conda install -n wmpl -y -c conda-forge numba
RUN conda install -n wmpl -y -c conda-forge libsqlite sqlite
RUN conda install -n wmpl -y -c conda-forge paramiko
RUN . /opt/miniconda3/etc/profile.d/conda.sh && conda activate wmpl && pip install "pymsis>=0.13"


COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH=./WesternMeteorPyLib
ENV PROJ_LIB=./
COPY *.py ./

COPY awskey[s] ./

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "wmpl", "python", "trajsolver.py"]