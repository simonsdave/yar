# to build the image
#
#   sudo docker build -t memcached_img .
#
# for testing/debugging
#
#   sudo docker run -i -t memcached_img /bin/bash
#
# spin up real nonnce store
#
#   MEMCACHED=$(sudo docker run -d memcached_img)
#   MEMCACHED_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $MEMCACHED)
#
# references
#
#   https://www.digitalocean.com/community/articles/docker-explained-how-to-create-docker-containers-running-memcached

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y memcached
