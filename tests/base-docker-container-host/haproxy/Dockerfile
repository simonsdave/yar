# to build the image
#
#   sudo docker build -t haproxy_img .
#
# for testing/debugging
#
#   sudo docker run -i -t -v /dev/log:/haproxy/log -v `pwd`:/haproxycfg haproxy_lb_img /bin/bash
# references
#
#   https://www.digitalocean.com/community/articles/how-to-use-haproxy-to-set-up-http-load-balancing-on-an-ubuntu-vps
#   https://github.com/1uptalent/dockerfiles/tree/master/haproxy-1.5

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

# at time of writing this installed version 1.4.18 of haproxy
RUN apt-get install -y haproxy

ADD haproxy.sh /usr/local/bin/haproxy.sh
RUN chown root.root /usr/local/bin/haproxy.sh

#
# https://launchpad.net/ubuntu/precise/+package/socat is a key tool
# for managing haproxy once it's up and running - see one of the articles
# below for an intro to the technique
#
# reference
# -- http://serverfault.com/questions/249316/how-can-i-remove-balanced-node-from-haproxy-via-c
#
apt-get install -y socat
