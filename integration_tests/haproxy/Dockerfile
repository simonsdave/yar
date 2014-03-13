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
