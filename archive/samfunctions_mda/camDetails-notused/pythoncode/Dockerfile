# Copyright (C) 2018-2023 Mark McIntyre
FROM public.ecr.aws/lambda/python:3.8

WORKDIR /app
COPY requirements.txt /app
RUN python3.8 -m pip install -r requirements.txt
ENV LD_LIBRARY_PATH /app:
#RUN pip install boto3

CMD ["camDetails.lambda_handler"]
