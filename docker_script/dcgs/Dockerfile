#MAINTAINER "Jay_Hung" 
FROM python:3.6


ARG VER=1.0 


RUN mkdir -p /tmp/DCGS


WORKDIR /tmp/DCGS


COPY ./src/requirement.txt .


RUN pip3 install -r ./requirement.txt




RUN apt-get update && apt-get install -y nano


RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata

RUN TZ=Asia/Taipei \ 
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata


RUN apt-get install xinetd telnetd -y

RUN apt-get install telnet -y
RUN apt-get install vim -y

RUN curl -sSL https://get.docker.com/ | sh

COPY ./ .
CMD python3 mainExternalGetService.py

