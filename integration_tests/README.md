yar integration testing is done by creating a series of
[Docker](https://www.docker.io/) containers to run
instances of the various yar services. The number, type
and size of these containers can be varied to validate
yar's operation in various deployment configurations.

The intended deployment OS for yar is
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and therefore the Docker containers used for integration
testing also run this OS.

The development environment for yar has been and
continues to be Mac OS X. Docker support for Mac OS X
is limited and thus a better supported Docker container
host is required for integration testsing.
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
was selected as the container host for integration testing.
[Vagrant](http://www.vagrantup.com/) is used to spin a
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/) virtual machine
running on [VirtualBox](https://www.virtualbox.org/)
acts as the container host.

Let's walk step by step through how to spin up an integration tests environment.
We'll assume you're doing this from ground zero and don't even have
the yar source installed on your machine.

* get the source code by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git; cd yar; source bin/cfg4dev
~~~~~

* provision the container host

~~~~~
cd integration_tests; ./provision_docker_container_host.sh
~~~~~

* it will take a few minutes, you'll see lots of messages rushing by on your
terminal windows as provision_docker_container_host.sh packages up yar
for install by pip, uses Vagrant to spin up a virtual machine
that's the container host on VirtualBox.
* once the virtual machine is running, use vagrant to ssh into the VM
and get to the directory in the VM that gives you access to the integration
test scripts

~~~~~
(env)>vagrant ssh
Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.2.0-23-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Welcome to your Vagrant-built virtual machine.
Last login: Fri Sep 14 06:23:18 2012 from 10.0.2.2
vagrant@precise64:~$ cd /vagrant
vagrant@precise64:/vagrant$ ls -la
total 36
drwxr-xr-x  1 vagrant vagrant  476 Feb 20 11:26 .
drwxr-xr-x 24 root    root    4096 Feb 20 11:27 ..
-rwxr-xr-x  1 vagrant vagrant  272 Feb 19 11:35 create_images.sh
drwxr-xr-x  1 vagrant vagrant  102 Feb 19 11:35 Key-Store
drwxr-xr-x  1 vagrant vagrant  102 Feb 19 11:35 Nonce-Store
-rwxr-xr-x  1 vagrant vagrant  553 Feb 19 12:02 provision_docker_container_host.sh
-rw-r--r--  1 vagrant vagrant  959 Feb 19 23:53 README.md
-rwxr-xr-x  1 vagrant vagrant  438 Feb 19 11:35 rm_all_containers.sh
-rwxr-xr-x  1 vagrant vagrant 3783 Feb 19 11:35 spin_up_deployment.sh
drwxr-xr-x  1 vagrant vagrant  102 Feb 19 11:50 .vagrant
-rw-r--r--  1 vagrant vagrant 4670 Feb 19 11:35 Vagrantfile
-rwxr-xr-x  1 vagrant vagrant  656 Feb 19 11:35 vagrant-provision.sh
drwxr-xr-x  1 vagrant vagrant  136 Feb 20 11:26 yar
vagrant@precise64:/vagrant$
~~~~~

* now let's create the Docker images that will host the various
yar services by running create_images.sh

~~~~~
./create_images.sh
~~~~~

* this will take several minutes to run as 3 Docker images are created - one
for the Key Store, a second for the Nonce Store and a final one for
the running the Auth Server, Key Server and App Server - use Docker's
images command to see the list of available images once create_images.sh
has completed

~~~~~
vagrant@precise64:/vagrant$ sudo docker images
REPOSITORY          TAG                 IMAGE ID            CREATED              VIRTUAL SIZE
yar_img             latest              c363428a22fa        About a minute ago   444.9 MB
key_store_img       latest              afab3edaa41d        4 minutes ago        562.9 MB
nonce_store_img     latest              11e067a8a011        8 minutes ago        265.5 MB
ubuntu              12.04               9cd978db300e        2 weeks ago          204.4 MB
~~~~~

* now we have everything we need to spin up a complete, simple yar deployment
and we'll do this using ./spin_up_deployment.sh

~~~~~
vagrant@precise64:/vagrant$ ./spin_up_deployment.sh
Starting Nonce Store
172.17.0.2:11211
Starting App Server
172.17.0.3:8080
Starting Key Store
172.17.0.4:5984/creds
Starting Key Server
172.17.0.5:8070
Starting Auth Server
172.17.0.6:8000

API key for basic auth = d6ff91ecd14d4da7b405ec6d6fe5c24d

MAC creds in auth = ~/.yar.creds
MAC_KEY_IDENTIFIER=992177d0305145a4ad4983f4e4b1b878
MAC_KEY=m-jHe4IcDTDVvL_acOIq0jYHFOYAh2pZErsUPpx1PTU
MAC_ALGORITHM=hmac-sha-1
~~~~~

* so what did ./spin_up_deployment.sh just do? it spun up
an [App Server](https://github.com/simonsdave/yar/wiki/App-Server),
a [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store),
a [Key Server](https://github.com/simonsdave/yar/wiki/Key-Server),
a [Nonce Store](https://github.com/simonsdave/yar/wiki/Nonce-Store) and
an [Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server) as well as
provisioning keys for [Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
and [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02)
* essentially this is a highly simplified but complete deployment of
yar that you can issue requests to using
[cURL](http://en.wikipedia.org/wiki/CURL) and
[yarcurl](https://github.com/simonsdave/yar/wiki/Utilities#yarcurl)
* you can see all the containers that are running using the docker ps command

~~~~~
vagrant@precise64:/vagrant$ sudo docker ps
CONTAINER ID        IMAGE                    COMMAND                CREATED             STATUS              PORTS               NAMES
74c06e96b101        yar_img:latest           auth_server --log=in   23 seconds ago      Up 22 seconds                           stoic_heisenberg
8fe347b3515a        yar_img:latest           key_server --log=inf   25 seconds ago      Up 24 seconds                           distracted_davinci
6801d6e051d4        key_store_img:latest     /bin/sh -c couchdb     3 minutes ago       Up 3 minutes        5984/tcp            pensive_wozniak
c3a6f1271403        yar_img:latest           app_server --log=inf   3 minutes ago       Up 3 minutes                            hopeful_bardeen
1b3900987e19        nonce_store_img:latest   /bin/sh -c memcached   4 minutes ago       Up 3 minutes        11211/tcp           berserk_engelbart
~~~~~

* from the host container try issuing some requests to the deployment

~~~~~
vagrant@precise64:/vagrant$ curl -s -u d6ff91ecd14d4da7b405ec6d6fe5c24d: http://172.17.0.6:8000/dave.html | jpp
{
    "auth": "YAR dave@example.com",
    "status": "ok",
    "version": "1.0",
    "when": "2014-02-23 23:04:53.857666"
}
~~~~~

* yar's [Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server),
[Key Server](https://github.com/simonsdave/yar/wiki/Key-Server)
and [Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server)
are all capabile of logging to
[syslog](http://manpages.ubuntu.com/manpages/precise/man8/rsyslogd.8.html)
(see the --syslog command line option for each of these servers)
* ./spin_up_deployment.sh maps the /dev/log device for each
[Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server),
[Key Server](https://github.com/simonsdave/yar/wiki/Key-Server)
and [Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server)
to the host container's /dev/log and tells these servers
to log to syslog which is useful because it means you can watch log output
for 3 servers by tailing /var/log/syslog on the container host

~~~~~
tail -f /var/log/syslog
~~~~~

* :TODO: data for key store containers
* as an aside, if at any point during the above you need to remove all
containers so you can start from scratch just run rm_all_containers.sh - just
be warned that rm_all_containers.sh kills all running containers and
removes all file systems for all containers - note the emphasis on "all" so
if you're running this directly on Ubuntu with non-yar docker containers
rm_all_containers.sh will remove them just as quickly as it removes
yar containers
