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
RUN wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

RUN apt-get install -y python-pip

RUN apt-get install -y libgmp-dev

RUN apt-get install -y python-dev

# note: source can be an http://... rule
ADD /vagrant/artifacts/tmp/yar-1.0.tar.gz /tmp

RUN pip install /tmp/yar-1.0.tar.gz

RUN rm /tmp/yar-1.0.tar.gz
