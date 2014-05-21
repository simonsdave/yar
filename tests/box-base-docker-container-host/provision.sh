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

# http://docs.docker.io/installation/ubuntulinux/
#
# Docker's logs are in /var/log/upstart/docker.log

apt-get update
apt-get install -y docker.io
ln -sf /usr/bin/docker.io /usr/local/bin/docker

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

sed -i 's/#DOCKER_OPTS="-dns 8.8.8.8 -dns 8.8.4.4"/DOCKER_OPTS="-e lxc"/g' /etc/default/docker.io

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
sudo docker build -t yarbase_img /vagrant/yarbase

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
# :TRICKY: "apt-get install -y python-pip" is the way I think
# we should be installing pip but on trusty apt-get installs
# pip 1.5.4 with which I couldn't figure out how to get rid
# of an error related to installing "tornado-memcache".
# Seemed like pip's i--allow-external option should have
# solved it but I couldn't get it to work. Long story to
# explain why easy_install is used to install pip
sudo easy_install pip==1.4.1

# install locust (https://github.com/locustio/locust)
#
# after upgrading to Ubuntu 14.04 from 12.04 and using
# "pip install locustio" to install locust started getting
# ImportError errors on 
# from requests.packages.urllib3.response import HTTPResponse
#
# as of the time of writing there were a few articles on
# the cause but limited info on a sol'n and hence the
# rather hacky approach used below

# locust built on gevent and gevent requires python-dev
# to be installed

apt-get install -y python-dev
# locustio requires pyzmq
apt-get install -y python-zmq

cd /tmp
git clone https://github.com/locustio/locust.git
cd locust
python setup.py sdist --formats=gztar
cd dist
pip install locustio-0.7.1.tar.gz

# these utilities are used to assemble graphs of load testing results
# can't just "apt-get install -y gnuplot" to install gnuplot because
# that installs version 4.4 which gets confused about where fonts
# are located on Ubuntu 12.04 so this means gnuplot has to be installed
# and built from source. found the link below a very helpful guide:
#
#   http://priyansmurarka.wordpress.com/2013/07/02/gnuplot-on-ubuntu-12-04/
#
apt-get install -y gnuplot

# install collectd 5.4 @ /usr/sbin/collectd
# config owned by root.root & @ /etc/collectd/collectd.conf
# to start collectd = sudo service collectd restart
# output @ /var/lib/collectd/csv/vagrant-ubuntu-trusty-64
apt-get install -y collectd

# socat (https://launchpad.net/ubuntu/precise/+package/socat) is a
# key command line tool for communicating with haproxy via a
# stats socket
#
# reference
# -- http://serverfault.com/questions/249316/how-can-i-remove-balanced-node-from-haproxy-via-command-line
#
apt-get install -y socat

# https://github.com/hopsoft/docker-graphite-statsd provided
# these instructions
#
# sudo docker run -i -t -p 3000:80 -p 2003:2003 -p 8125:8125/udp -v /var/log/graphite:/var/log -v /opt/graphite/storage -v /opt/graphite/conf hopsoft/graphite-statsd bash
#
# use Vagrant forward port 9000 to port 3000 and Graphite will
# be available on http://127.0.0.1:9000
#
# cd /tmp
# git clone https://github.com/hopsoft/docker-graphite-statsd.git
# cd docker-graphite-statsd
# sudo docker build -t hopsoft/graphite-statsd .
# sudo mkdir /var/log/graphite

# at the start of this script several changes were made
# to boot parameters. let's quickly restart the VM so
# these changes take effect

shutdown -r now
