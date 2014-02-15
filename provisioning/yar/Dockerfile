# this Dockerfile creates a base image for all yar servers
# all the python pre-reqs are installed and the yar package
# is also installed
#
# to build the image
#
#   sudo docker build -t yar_img .
#
# these are very useful for interactive testing/debugging
#
#   sudo docker run -i -t yar_img /bin/bash
#   C1=$(sudo docker run -name yar_001 -d yar_img)
#   C1_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $C1)
#
# app server
#
#   APPS_001=$(sudo docker run -d -p 8080:8080 -name apps_001 yar_img app_server --log=info --lon=8080)
#   APPS_001_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $APPS_001)
#   curl http://$APPS_001_IP:8080/dave.html
#
#   KS1=$(sudo docker run -d -p 8070:8070 -name ks_001 yar_img key_server --log=info --lon=8070)
#   KS1_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $KS1)
#   docker run -d -p 8001:8001 -p 5001:5001 coreos/etcd -peer-addr ${PUBLIC_IP}:8001 -addr ${PUBLIC_IP}:5001 -name etcd-node1
#
# Using apache benchmark (http://httpd.apache.org/docs/2.2/programs/ab.html)
# to drive load thru the deployment
#
#   ab -c 100 -n 1000 http://$APPS_001_IP:8080/dave.html
#
#       -c = concurrency level
#       -n = # of requests
#       -v = verbosity level (2, 3, 4)

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
