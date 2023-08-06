FROM python:3.11-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y fortune-mod

COPY typer.py .

CMD [ "python3", "./typer.py" ]
