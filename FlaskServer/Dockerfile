#syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder

WORKDIR /code

COPY requirements.txt /code
RUN pip3 install -r requirements.txt

COPY . /code

EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["app.py"]
