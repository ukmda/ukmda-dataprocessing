# Copyright (C) 2018-2023 Mark McIntyre#
FROM public.ecr.aws/lambda/python:3.8
RUN yum -y update
RUN pip install --upgrade pip
WORKDIR /app
COPY requirements.txt /app
RUN python3.8 -m pip install -r requirements.txt
ENV LD_LIBRARY_PATH /app:
RUN pip install boto3
COPY . /app
EXPOSE 80

ENTRYPOINT ["python", "flaskapp.py"]
