FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y fortune-mod
RUN apt-get install -y python3

ADD main.py .

CMD [ "python3", "./main.py" ]
