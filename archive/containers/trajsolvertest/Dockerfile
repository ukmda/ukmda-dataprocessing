FROM continuumio/miniconda3

COPY requirements.txt ./
RUN conda install -y -c conda-forge numpy scipy matplotlib cython pytz pyqt
RUN conda install -y -c conda-forge jplephem ephem
RUN conda install -y -c conda-forge basemap basemap-data-hires
RUN conda install -y -c conda-forge pandas cartopy

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./
RUN pip install boto3
COPY *.py ./

ENTRYPOINT ["python", "trajsolver.py"]
