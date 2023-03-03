FROM public.ecr.aws/lambda/python:3.8
RUN yum -y update
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./:

RUN pip install boto3
COPY *.py ./
EXPOSE 80

ENTRYPOINT ["python", "flaskapp.py"]
