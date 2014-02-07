# sudo docker build -t memcached_img .

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y memcached

EXPOSE 11211

CMD ["-m", "128"]

USER daemon

ENTRYPOINT memcached
