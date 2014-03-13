#!/usr/bin/env bash

apt-get update

apt-get install -y linux-image-generic-lts-raring linux-headers-generic-lts-raring
apt-get install -y virtualbox-guest-utils

sudo shutdown -r now
