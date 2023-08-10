FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache fortune

COPY typer.py .

CMD [ "python3", "./typer.py" ]
