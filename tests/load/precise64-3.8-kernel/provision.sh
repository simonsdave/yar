#!/usr/bin/env bash

apt-get update

apt-get install -y linux-image-generic-lts-raring linux-headers-generic-lts-raring
apt-get install -y virtualbox-guest-utils

# based on http://docs.docker.io/en/latest/installation/ubuntulinux/
# tell kernel to collect memory metrics - this is disabled by default
#
# for a more complete story on container monitoring see
# http://blog.docker.io/2013/10/gathering-lxc-docker-containers-metrics/
sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"/g' /etc/default/grub

shutdown -r now
