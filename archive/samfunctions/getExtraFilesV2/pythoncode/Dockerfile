# Copyright (C) 2018-2023 Mark McIntyre

FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt -t .
RUN python -m pip install numba watchdog basemap-data-hires -t .
RUN python -m pip install cartopy -t .
#RUN yum update -y
ENV LD_LIBRARY_PATH=./
COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
#COPY *.npy ./WesternMeteorPyLib/wmpl/share/
COPY *.py ./
ENV PYTHONPATH=./WesternMeteorPyLib
ENV PROJ_LIB=./

CMD ["getExtraFiles.lambda_handler"]
