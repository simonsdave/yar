#!/usr/bin/env bash

#
# build all docker images
#
sudo docker build -t yar_img /vagrant

#
# install yar
#
sudo pip install /vagrant/yar-1.0.tar.gz
