# installs couchdb 1.5 from source. this is required since
# apt-get install -y couchdb installs version 1.2
#
# create image
#   sudo docker build -t key_store_img .
#
# get key store running
#   KEY_STORE_001=$(sudo docker run -name key_store_001 -d key_store_img)
#   KEY_STORE_001_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $KEY_STORE_001)
# very useful for interactive testing/debugging
#
#   sudo docker run -i -t ubuntu:12.04 /bin/bash
#
# references
#   http://deepuelenor.wordpress.com/2013/12/13/installing-latest-version-of-couchdb-1-5-0-on-ubuntu-12-04-lts/
#   https://wiki.apache.org/couchdb/Installing_on_Ubuntu

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y couchdb

EXPOSE 5984

USER daemon

ENTRYPOINT couchdb
