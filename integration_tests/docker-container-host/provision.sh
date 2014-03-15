#!/usr/bin/env bash

apt-get update

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

# simple command line tools for poking @ memcached
apt-get install -y libmemcached-tools

# :TODO: reminder - docker recommends updating linux kernel - who to do this?

# http://docs.docker.io/en/latest/installation/ubuntulinux/#ubuntu-precise-12-04-lts-64-bit
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
apt-get update
# as of 12 Mar this installs docker 0.9
# :TODO: how do versions get controlled with apt-get?
apt-get install -y lxc-docker

# python scripts setup and drive tests so we'll need pip
apt-get install -y python-pip

# why do we need make?
apt-get install -y make

# Locust is built on gevent and gevent requires python-dev
# to be installed
apt-get install -y python-dev

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
apt-get install -y imagemagick
