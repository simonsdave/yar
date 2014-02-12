# this Dockerfile creates a base image for all yar servers
# all the python pre-reqs are install and the yar package
# is also installed
#
# usage
#
#   sudo docker build -t yar_img .

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y wget

# don't like doing having the --no-check-certificate
RUN wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

RUN apt-get install -y python-pip

# these next 3 need to be install because yar uses keyczar

# unclear why if a vagrant ubuntu 12.04 install has gcc
# that a docker based install of ubuntu 12.04 needs to
# have gcc installed
RUN apt-get install -y gcc
RUN apt-get install -y libgmp-dev
RUN apt-get install -y python-dev

# :TRICKY: ADD command decompresses the archive and extract
# all the files in the archive
ADD yar-1.0.tar.gz /tmp/.

RUN pip install /tmp/yar-1.0
