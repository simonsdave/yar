Testing and experimenting with a full yar deployment
is done by creating a series of
[Docker](https://www.docker.io/) containers to run
instances of the various yar services. The number, type
and size of these containers can be varied to validate
yar's operation in various deployment configurations.

The intended deployment OS for yar is
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and therefore the Docker containers used for integration
testing also run this OS.

The primary development environment for yar has been, and
continues to be, Mac OS X. Docker support for Mac OS X
is limited and thus a better supported Docker container
host is required for testsing.
Again, [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
was selected as the container host.
[Vagrant](http://www.vagrantup.com/) is used to spin a
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
on [VirtualBox](https://www.virtualbox.org/)
as the container host.

Let's walk step by step through the process of spinning up a deployment.
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
and get to the directory that gives you access to the 
testing scripts

~~~~~
(env)>vagrant ssh
Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.2.0-23-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Welcome to your Vagrant-built virtual machine.
Last login: Fri Sep 14 06:23:18 2012 from 10.0.2.2
vagrant@precise64:~$ cd /vagrant
vagrant@precise64:/vagrant$ ls -la
total 68
drwxr-xr-x  1 vagrant vagrant   748 Mar  1 12:42 .
drwxr-xr-x 24 root    root     4096 Mar  1 12:43 ..
drwxr-xr-x  1 vagrant vagrant   170 Feb 28 23:19 App-Server-LB
drwxr-xr-x  1 vagrant vagrant   136 Mar  1 12:42 artifacts
drwxr-xr-x  1 vagrant vagrant   170 Mar  1 12:24 Auth-Server-LB
-rwxr-xr-x  1 vagrant vagrant   408 Mar  1 12:36 create_images.sh
-rw-r--r--  1 vagrant vagrant  6148 Feb 28 20:34 .DS_Store
-rwxr-xr-x  1 vagrant vagrant    25 Feb 28 20:47 .gitignore
drwxr-xr-x  1 vagrant vagrant   136 Feb 28 23:19 Key-Store
drwxr-xr-x  1 vagrant vagrant   102 Feb 27 22:56 Nonce-Store
-rw-r--r--  1 vagrant vagrant  1239 Feb 28 14:37 plot_load_test_results
-rwxr-xr-x  1 vagrant vagrant  2171 Feb 28 17:10 provision_docker_container_host_post_vagrant_up.sh
-rwxr-xr-x  1 vagrant vagrant   685 Feb 27 22:56 provision_docker_container_host.sh
-rw-r--r--  1 vagrant vagrant 10791 Feb 27 22:56 README.md
-rwxr-xr-x  1 vagrant vagrant   438 Feb 27 22:56 rm_all_containers.sh
-rwxr-xr-x  1 vagrant vagrant  3441 Feb 28 23:07 run_load_test.sh
-rwxr-xr-x  1 vagrant vagrant  7851 Feb 28 22:35 spin_up_deployment.sh
drwxr-xr-x  1 vagrant vagrant   136 Feb 27 22:56 SSL-Term
drwxr-xr-x  1 vagrant vagrant   374 Feb 28 23:07 test-results
drwxr-xr-x  1 vagrant vagrant   102 Feb 27 22:57 .vagrant
-rw-r--r--  1 vagrant vagrant  4700 Mar  1 12:24 Vagrantfile
drwxr-xr-x  1 vagrant vagrant   136 Mar  1 12:42 yar
vagrant@precise64:/vagrant$
~~~~~

* now let's create the Docker images for
yar services by running create_images.sh

~~~~~
./create_images.sh
~~~~~

* this will take several minutes to run as 5 Docker images are created - one
for each of the Key Store, the Nonce Store, load balancer for the Auth Servers,
the load balancer for App Servers and a final one for
the running the Auth Server, Key Server and App Server - use Docker's
images command to see the list of available images once create_images.sh
has completed

~~~~~
vagrant@precise64:/vagrant$ sudo docker images
REPOSITORY           TAG                 IMAGE ID            CREATED              VIRTUAL SIZE
yar_img              latest              1c8045e67082        41 seconds ago      444.9 MB
key_store_img        latest              3165591d3b4e        3 minutes ago       563 MB
nonce_store_img      latest              3d11114f6091        7 minutes ago       265.5 MB
auth_server_lb_img   latest              8b3c3e0be13f        8 minutes ago       226 MB
app_server_lb_img    latest              8b3c3e0be13f        8 minutes ago       226 MB
ubuntu               12.04               9cd978db300e        3 weeks ago         204.4 MB
~~~~~

* now we have everything we need to spin up a complete, simple yar deployment
and we'll do this using ./spin_up_deployment.sh

~~~~~
vagrant@precise64:/vagrant$ ./spin_up_deployment.sh
Creating Services ...

Starting App Server(s)
172.17.0.2:8080
Starting App Server LB
172.17.0.3:8080
Starting Nonce Store
172.17.0.4:11211
Starting Key Store
172.17.0.5:5984/creds
Starting Key Server
172.17.0.6:8070
Starting Auth Server
172.17.0.7:8000
Starting Auth Server LB
172.17.0.8:8000

Creating Credentials ...

Credentials in ~/.yar.creds
API_KEY=bcca8cf60c8042a0a098486be74a1b32
MAC_KEY_IDENTIFIER=147751cc8b8f4007ba12e4aeacc9a5bc
MAC_KEY=rb5C1RVB29EtnvU8eGms_ZwKzBv_mMU54FeKZTxEi78
MAC_ALGORITHM=hmac-sha-1
~~~~~

* so what did ./spin_up_deployment.sh just do? it spun up a
highly simplified but complete deployment of yar
* you can see all the running services using docker's ps command

~~~~~
vagrant@precise64:/vagrant$ sudo docker ps
CONTAINER ID        IMAGE                      COMMAND                CREATED              STATUS              PORTS               NAMES
245d71b20960        app_server_lb_img:latest   haproxy -f /haproxyc   37 seconds ago       Up 36 seconds                           hungry_lumiere
a48896a577d3        yar_img:latest             auth_server --log=in   38 seconds ago       Up 38 seconds                           drunk_einstein
7941d4098e9d        yar_img:latest             key_server --log=inf   39 seconds ago       Up 39 seconds                           backstabbing_engelbart
5220789c8bae        key_store_img:latest       /bin/sh -c couchdb     57 seconds ago       Up 57 seconds       5984/tcp            thirsty_galileo
de29033b58c5        nonce_store_img:latest     /bin/sh -c memcached   58 seconds ago       Up 58 seconds       11211/tcp           stupefied_lovelace
b5e9f99d6404        app_server_lb_img:latest   haproxy -f /haproxyc   About a minute ago   Up 59 seconds                           berserk_ptolemy
e3f638c85c23        yar_img:latest             app_server --log=inf   About a minute ago   Up About a minute                       jovial_tesla
~~~~~

* spin_up_deployment.sh also 
provisioned keys for [Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
and [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02)
authentication
* you can issue requests to using
[cURL](http://en.wikipedia.org/wiki/CURL) and
[yarcurl](https://github.com/simonsdave/yar/wiki/Utilities#yarcurl) - go ahead, try it

~~~~~
vagrant@precise64:/vagrant$ curl -s -u bcca8cf60c8042a0a098486be74a1b32: http://172.17.0.8:8000/dave.html | jpp
{
    "auth": "YAR dave@example.com",
    "status": "ok",
    "when": "2014-03-01 13:23:36.066555"
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

* above we issued request to the deployment using
[cURL](http://en.wikipedia.org/wiki/CURL) and
[yarcurl](https://github.com/simonsdave/yar/wiki/Utilities#yarcurl) but if
you want to get a sense of how yar performs under load you'll
want to issue repeated requests at various concurrency levels - a simple
way to get going down that path is to use
[Apache's ab](http://httpd.apache.org/docs/2.4/programs/ab.html) utility which
was installed on the container host by provision_docker_container_host.sh - below
is an example of using ab to issue 10,000 requests to the deployment's
auth server 10 requests at a time

~~~~~
vagrant@precise64:/vagrant$ ab -c 10 -n 10000 -A 5eed597374994bd0a078552208799434: http://172.17.0.6:8000/dave.html
This is ApacheBench, Version 2.3 <$Revision: 655654 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 172.17.0.6 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        TornadoServer/3.0.1
Server Hostname:        172.17.0.6
Server Port:            8000

Document Path:          /dave.html
Document Length:        104 bytes

Concurrency Level:      10
Time taken for tests:   142.237 seconds
Complete requests:      10000
Failed requests:        7
   (Connect: 0, Receive: 0, Length: 7, Exceptions: 0)
Write errors:           0
Non-2xx responses:      7
Total transferred:      3069112 bytes
HTML transferred:       1039272 bytes
Requests per second:    70.31 [#/sec] (mean)
Time per request:       142.237 [ms] (mean)
Time per request:       14.224 [ms] (mean, across all concurrent requests)
Transfer rate:          21.07 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    8 463.9      0   31038
Processing:    38  134 532.1    121   20086
Waiting:       38  134 532.1    121   20086
Total:         38  142 720.5    121   31161

Percentage of the requests served within a certain time (ms)
  50%    121
  66%    126
  75%    129
  80%    130
  90%    136
  95%    142
  98%    149
  99%    156
 100%  31161 (longest request)
~~~~~

* :TODO: data for key store containers
* as an aside, if at any point during the above you need to remove all
containers so you can start from scratch just run rm_all_containers.sh - just
be warned that rm_all_containers.sh kills all running containers and
removes all file systems for all containers - note the emphasis on "all" so
if you're running this directly on Ubuntu with non-yar docker containers
rm_all_containers.sh will remove them just as quickly as it removes
yar containers

Notes
-----
* why are bash scripts used for lots of this testing? why not use Python
and docker-py? tried docker-py but found the API really poorly documented
and not used extensively (so Googling for answers yielded few hits).
The docker cli on the other hand is very well documented and lots of folks
are using it so easy to Google for answers.
