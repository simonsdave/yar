# to build the image
#
#   sudo docker build -t nonce_store_img .
#
# for testing/debugging
#
#   sudo docker run -i -t nonce_store_img /bin/bash
#
# spin up real nonnce store
#
#   NONCE_STORE=$(sudo docker run -d nonce_store_img)
#   NONCE_STORE_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $NONCE_STORE)
#
# references
#
#   https://www.digitalocean.com/community/articles/docker-explained-how-to-create-docker-containers-running-memcached

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y memcached

EXPOSE 11211

CMD ["-m", "128"]

USER daemon

ENTRYPOINT memcached
