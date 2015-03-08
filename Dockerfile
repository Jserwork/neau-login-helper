FROM python:2

RUN \
  cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
  echo "deb http://mirrors.aliyun.com/debian/ wheezy main non-free contrib" > /etc/apt/sources.list && \
  echo "deb http://mirrors.aliyun.com/debian/ wheezy-proposed-updates main non-free contrib" >> /etc/apt/sources.list && \
  echo "deb-src http://mirrors.aliyun.com/debian/ wheezy main non-free contrib" >> /etc/apt/sources.list && \
  echo "deb-src http://mirrors.aliyun.com/debian/ wheezy-proposed-updates main non-free contrib" >> /etc/apt/sources.list

RUN apt-get update

RUN apt-get install -y supervisor

RUN pip install tornado
RUN pip install pillow

RUN mkdir -p /var/log/supervisor

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 7777

CMD ["/usr/bin/supervisord"]
