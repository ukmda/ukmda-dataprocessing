# Copyright (C) 2018-2023 Mark McIntyre
FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .
RUN yum update -y
ENV LD_LIBRARY_PATH ./
COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
COPY *.npy ./WesternMeteorPyLib/wmpl/share/
COPY *.py ./
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./

CMD ["getExtraFiles.lambda_handler"]
