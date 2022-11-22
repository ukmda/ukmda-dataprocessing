FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./
COPY *.py ./
COPY *.csv ./

CMD ["ftpToUkmon1.lambda_handler"]
