# sudo docker build -t memcached_img .
# NS1=$(sudo docker run -name memcached_ins_001 -d memcached_img)
# NS1_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $NS1)

FROM ubuntu:12.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y memcached

EXPOSE 11211

CMD ["-m", "128"]

USER daemon

ENTRYPOINT memcached
