# this Dockerfile creates a base image for all yar servers
# all the python pre-reqs are installed and the yar package
# is also installed
#
# to build the image
#
#   sudo docker build -t yarbase_img .
#
# useful for interactive testing/debugging
#
#   sudo docker run -i -t yarbase_img /bin/bash

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y python-setuptools

RUN apt-get install -y python-pip

# these next 4 need to be install because yar uses keyczar
#
# :TODO: the "apt-get update" was added after the gcc install
# started failing (~8 May '14). unclear why the "apt-get update"
# fixes the problem but it did. need to understand.
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libgmp-dev
RUN apt-get install -y python-dev
