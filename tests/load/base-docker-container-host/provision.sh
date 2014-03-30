#!/usr/bin/env bash

#
# this script is intended to be called by Vagrant when provisioning
# the docker container host
#

apt-get update

# :TODO: not sure I totally get this, until Docker 0.9 I believe lxc was
# installed by Docker but this no longer seems to be the case so we're
# manually installing it before Docker is installed
apt-get install -y lxc

# http://docs.docker.io/en/latest/installation/ubuntulinux/#ubuntu-precise-12-04-lts-64-bit
#
# probably useful to know that Docker's logs are in /var/log/upstart/docker.log

apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
apt-get update
# as of 12 Mar this installs docker 0.9
# :TODO: how do versions get controlled with apt-get?
apt-get install -y lxc-docker

# force Docker to use the lxc execution engine because (as per
# http://blog.docker.io/2013/10/gathering-lxc-docker-containers-metrics/)
# we want to get access to things like CPU and memory usage metrics
# using cgroups. with Docker 0.9 they've introduced something
# (that I don't understand) which disables the cgroups stuff.
#
# to convince yourself that this is working the following should help
#
# run this command
#
#   ls -la /sys/fs/cgroup/memory/lxc
#
# and won't see any container IDs
#
# start a container running in the background (not it's gotta be
# in the background otherwise the cgroup psudeo-files won't be there)
#
#   CONTAINER_ID=$(sudo docker run -d ubuntu /bin/sh -c "while true; do echo $(date) - hello world; sleep 1; done")
#
# convince yourself the container is running by doing something like
#
#   sudo docker logs $CONTAINER_ID
#
# now try the ls again this time attempting to get the memory
# currently being used by the container
#
#   ls -la /sys/fs/cgroup/memory/lxc/$CONTAINER_ID/memory.usage_in_bytes

sed -i 's/#DOCKER_OPTS="-dns 8.8.8.8 -dns 8.8.4.4"/DOCKER_OPTS="-e lxc"/g' /etc/default/docker

# based on http://docs.docker.io/en/latest/installation/ubuntulinux/
# tell kernel to collect memory metrics - this is disabled by default
#
# for a more complete story on container monitoring see
# http://blog.docker.io/2013/10/gathering-lxc-docker-containers-metrics/

sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="cgroup_enable=memory"/g' /etc/default/grub

#
# build all docker images that don't depend on yar specific code
#

sudo docker build -t memcached_img /vagrant/memcached
sudo docker build -t haproxy_img /vagrant/haproxy
sudo docker build -t couchdb_img /vagrant/couchdb

# curl's a generally useful utility across SO many platforms ...
apt-get install -y curl

# we're going to need git to grab some projects from github
apt-get install -y git

# JSON.sh is a json parser written in bash
cd /tmp
git clone https://github.com/dominictarr/JSON.sh.git
cd JSON.sh
mv JSON.sh /usr/local/bin/.
cd

# for apache benchmark
# http://httpd.apache.org/docs/2.2/programs/ab.html
apt-get install -y apache2-utils

# python scripts setup and drive tests so we'll need pip
apt-get install -y python-pip

# why do we need make?
apt-get install -y make

# Locust is built on gevent and gevent requires python-dev
# to be installed
apt-get install -y python-dev

# pyzmq requires Cython
# pip install Cython
# locustio requires pyzmq
apt-get install python-zmq
# pip install pyzmq

# Locust is a modern Python based load generator.
# Either Apache Benchmark or Locust are used to
# load/stress a yar deployment.
pip install locustio

# these utilities are used to assemble graphs of load testing results
# can't just "apt-get install -y gnuplot" to install gnuplot because
# that installs version 4.4 which gets confused about where fonts
# are located on Ubuntu 12.04 so this means gnuplot has to be installed
# and built from source. found the link below a very helpful guide:
#
#   http://priyansmurarka.wordpress.com/2013/07/02/gnuplot-on-ubuntu-12-04/
apt-get install -y libwxgtk2.8-dev libpango1.0-dev libx11-dev libxt-dev texinfo
cd /tmp
curl -O ftp://ftp.dante.de/pub/tex/graphics/gnuplot/4.6.5/gnuplot-4.6.5.tar.gz
tar xvf gnuplot-4.6.5.tar.gz
cd gnuplot-4.6.5
./configure
make
make check
make install

# this is needed for getting the convert utility that allows multiple
# images to be combined into a single pdf at the end of the load test
# as well as a bunch of other image manipulation magic
apt-get install -y imagemagick

# at the start of this script several changes were made
# to boot parameters. let's quickly restart the VM so
# these changes take effect

shutdown -r now
