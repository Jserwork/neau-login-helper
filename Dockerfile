FROM python:2

RUN apt-get update

RUN apt-get install -y supervisor

RUN pip install tornado
RUN pip install pillow

RUN mkdir -p /var/log/supervisor

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["/usr/bin/supervisord"]
