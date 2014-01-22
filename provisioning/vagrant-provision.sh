#!/usr/bin/env bash

apt-get install -y python-pip
apt-get install -y python-setuptools
# cd /tmp
# wget -q - http://python-distribute.org/distribute_setup.py
# python distribute_setup.py
# apt-get install -y python-virtualenv

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
gunzip yar-*.*.tar.gz
tar xvf yar-*.*.tar
cd yar-*.*
sudo python setup.py install
cd /tmp
rm -rf yar-*.*. >& /dev/null

echo "############################################################"
echo "Creating yar user"
echo "############################################################"
useradd --system --user-group --create-home yar

echo "############################################################"
