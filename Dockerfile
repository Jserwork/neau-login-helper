FROM python:2-alpine3.6

RUN apk update
RUN apk add build-base
RUN apk add jpeg-dev
RUN apk add zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

ENV PYTHONUNBUFFERED 1

RUN pip install tornado
RUN pip install pillow

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
EXPOSE 18080

CMD ["python2", "index.py"]
