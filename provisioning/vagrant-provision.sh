#!/usr/bin/env bash

apt-get update

# run 2 x lines below if we need setuptools 2.1 rather than the 0.6 default
cd /tmp
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

apt-get install -y python-pip

# libgmp-dev installed to avoid the warning
#   "warning: GMP or MPIR library not found; Not building Crypto.PublicKey._fastmath."
# when install pycrypto
apt-get install -y libgmp-dev

# installing python-dev was req'd because pycrypto install was failing
# when trying to install clf's setup.py - the article below describes
# the problem and sol'n
# http://stackoverflow.com/questions/11596839/install-pycrypto-on-ubuntu
apt-get install -y python-dev

echo "############################################################"
echo "Installing yar server(s), cli and frameworks"
echo "############################################################"
# :TODO: in future, there should service specific setup.py
cd /tmp
cp /vagrant/artifacts/tmp/yar-*.*.tar.gz .
pip install yar-*.*.tar.gz
cd /tmp
rm -rf yar-*.*. >& /dev/null

echo "############################################################"
echo "Creating yar user"
echo "############################################################"
useradd --system --user-group --create-home yar

echo "############################################################"
echo "Installing docker"
echo "############################################################"
# http://docs.docker.io/en/latest/installation/ubuntulinux/#ubuntu-precise-12-04-lts-64-bit
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
apt-get update
apt-get install -y lxc-docker

echo "############################################################"
echo "Get nonce store running"
echo "############################################################"

# nice reference for getting memcached running using docker 
#   https://www.digitalocean.com/community/articles/docker-explained-how-to-create-docker-containers-running-memcached

cp -r /vagrant/Nonce-Store .
cd Nonce-Store
docker build -t memcached_img .
NS1=$(sudo docker run -name memcached_ins_001 -d memcached_img)
NS1_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $NS1)
echo $NS1
echo $NS1_IP

apt-get install wget
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
apt-get install -y python-pip
apt-get install -y libgmp-dev
apt-get install -y python-dev

echo "############################################################"
