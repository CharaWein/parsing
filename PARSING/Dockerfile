FROM python:3.12
MAINTAINER Weinmaier Andrew
LABEL version="0.42"

WORKDIR /serv

EXPOSE 4000

COPY ./requirements.txt /serv/requirements.txt

RUN pip install -r requirements.txt 

COPY . .

RUN chmod 777 cgi-bin/database.db

ENTRYPOINT ["/usr/bin/python3", "./start_server.py"]