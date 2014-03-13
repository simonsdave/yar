############################################################
# Dockerfile to build ...
#
# sudo docker build -t nginx_img .
############################################################

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN echo "deb http://archive.ubuntu.com/ubuntu/ raring main universe" >> /etc/apt/sources.list

RUN apt-get update

# :TODO: this really needed?
RUN apt-get install -y nano wget dialog net-tools

RUN apt-get install -y nginx

RUN rm -v /etc/nginx/nginx.conf

ADD nginx.conf /etc/nginx/

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

EXPOSE 80

CMD service nginx start

