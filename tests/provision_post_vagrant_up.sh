#!/usr/bin/env bash

#
# these utilities are exceptionally useful during
# load/stress testing in the container host
#
cp /vagrant/artifacts/jpp /usr/local/bin/.
cp /vagrant/artifacts/yarcurl /usr/local/bin/.

#
# build all docker images
#
sudo docker build -t yar_img /vagrant/yar
