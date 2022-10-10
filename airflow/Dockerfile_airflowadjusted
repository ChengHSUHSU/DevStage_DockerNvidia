FROM apache/airflow:2.0.2

ENV PYTHONPATH "${PYTHONPATH}:/home/python_modules:/opt/airflow/dags"

USER root
RUN pip install docker

RUN curl -sSL https://get.docker.com/ | sh
ENV SHARE_DIR /usr/local/share
