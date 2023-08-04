FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y fortune-mod
RUN apt-get install -y python3

ADD typer.py .

CMD [ "python3", "./typer.py" ]
