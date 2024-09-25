#docker build -t webis/tira:tira-data-0.0.1 .
FROM python:3

RUN pip3 install tira click

ADD data/dist /dist
