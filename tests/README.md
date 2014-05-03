Testing against and experimenting with a full yar deployment
is done by creating a series of
[Docker](https://www.docker.io/) containers which run
instances of the various yar services. The number, type
and size of these containers can be varied when the deployment
is spun up to validate yar's operation in a variety of
deployment configurations. Also, after initial deployment
is up and running, it is also possible to add and remove
services to understand and verify a broad set of
operational scenarios.

* spin up a [VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and version 3.8 of the Linux kernel

Creating a Box with Correct Linux Kernel
----------------------------------------

The primary development environment for yar is
[Mac OS X](http://www.apple.com/ca/osx/).
[Docker](https://www.docker.io/) doesn't support
[Mac OS X](http://www.apple.com/ca/osx/)
so a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 12.04](http://releases.ubuntu.com/12.04/) is
used as the [Docker](https://www.docker.io/) container host. 
There's one little gotcha to address = the default
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
[box](http://docs.vagrantup.com/v2/boxes.html)
runs the 3.2 Linux kernel but 
[Docker requires](http://docs.docker.io/en/latest/installation/ubuntulinux/)
version 3.8 of the Linux kernel. So, we need create a local
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
[box](http://docs.vagrantup.com/v2/boxes.html)
with the 3.8 Linux kernel.

* [these instructions](precise64-3.8-kernel/README.md) describe how to create
a [box](http://docs.vagrantup.com/v2/boxes.html) called *precise64-3.8-kernel*
and make the [box](http://docs.vagrantup.com/v2/boxes.html)
available in the local [box](http://docs.vagrantup.com/v2/boxes.html) repo

> NOTE - creating the [box](http://docs.vagrantup.com/v2/boxes.html)
with the right kernel version is a one time operation - you don't have
to do this before running each load test - create the
[box](http://docs.vagrantup.com/v2/boxes.html)
once and reuse it again and again

Creating a Base Docker Container Host
-------------------------------------

We now have a [box](http://docs.vagrantup.com/v2/boxes.html) with the right
version of the kernel on which we can build a Base Docker Container Host.

* [these instructions](base-docker-container-host/README.md) describe how to create
a [box](http://docs.vagrantup.com/v2/boxes.html) called *docker-container-host*
and make the [box](http://docs.vagrantup.com/v2/boxes.html)
available in the local [box](http://docs.vagrantup.com/v2/boxes.html) repo

> NOTE - creating the Base Docker Container Host
[box](http://docs.vagrantup.com/v2/boxes.html)
is a one time operation - you don't have
to do this before running each load test - create the
[box](http://docs.vagrantup.com/v2/boxes.html)
once and reuse it again and again

Creating a Docker Container Host
--------------------------------

Using the above instructions you created a Base Docker Container Host
as a [Vagrant](http://www.vagrantup.com/)
[box](http://docs.vagrantup.com/v2/boxes.html)
running [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and called it base-docker-container-host.
This [box](http://docs.vagrantup.com/v2/boxes.html) has
90% of what we need to run a load test.
The steps below finish creation of the Docker Container Host.
In the steps below we'll assume you've got the yar source
installed at ~/yar.

* first let's get to the right directory

~~~~~
cd; cd yar; source bin/cfg4dev; cd tests/load
~~~~~

* spin up the [box](http://docs.vagrantup.com/v2/boxes.html)

> NOTE - to spin up the the [box](http://docs.vagrantup.com/v2/boxes.html),
> [provision.sh](provision.sh) is used rather than
> [vagrant up](https://docs.vagrantup.com/v2/cli/up.html)

~~~~~
(env)>./provision.sh
<<<cut lots of messages>>>
Cleaning up...
 ---> 296a0d185246
Successfully built 296a0d185246
Removing intermediate container 5a44c1ec3b91
Removing intermediate container 982f1a0f2c5c
Removing intermediate container ffe5092ef8a5
Removing intermediate container 886099a5276f
Removing intermediate container 30ad71f4f716
Removing intermediate container 2847bcb40322
Removing intermediate container a877af84d9d1
Removing intermediate container d984d433d10b
(env)>
~~~~~

* once the VM is running, ssh into the VM

~~~~~
(env)>vagrant ssh
Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.8.0-38-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Welcome to your Vagrant-built virtual machine.
Last login: Fri Sep 14 06:23:18 2012 from 10.0.2.2
vagrant@precise64:~$
~~~~~

* now you'll be able to see the [Docker](https://www.docker.io/)
images that will be used to create [Docker](https://www.docker.io/)
containers that will be used for load testing yar
* to see the [Docker](https://www.docker.io/) images use
the docker images command

~~~~~
vagrant@precise64:~$ sudo docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
yar_img             latest              e9fe52ca3e07        59 seconds ago      445.3 MB
couchdb_img         latest              3c98699e421f        30 minutes ago      563.4 MB
haproxy_img         latest              6b12916c8aa7        33 minutes ago      226.4 MB
memcached_img       latest              e527fd882aab        33 minutes ago      265.9 MB
ubuntu              12.04               9cd978db300e        8 weeks ago         204.4 MB
~~~~~

Congratulations! You now have everything that's necessary to 
run some load tests:-)

Running Load Tests
------------------

:TODO: these instructions need updating ...

~~~~~
vagrant@precise64:/vagrant$ ./spin_up_deployment.sh
Starting Services ...

Starting App Server(s)
172.17.0.2:8080 in /tmp/tmp.qsomtrJz1H/App-Server
Starting App Server LB
172.17.0.3:8080 in /tmp/tmp.qsomtrJz1H/App-Server-LB
Starting Nonce Store
172.17.0.4:11211
Starting Key Store
172.17.0.5:5984/creds in /tmp/tmp.qsomtrJz1H/Key-Store
Starting Key Server
172.17.0.6:8070 in /tmp/tmp.qsomtrJz1H/Key-Server
Starting Auth Server
172.17.0.7:8000 in /tmp/tmp.qsomtrJz1H/Auth-Server
Starting Auth Server LB
172.17.0.8:8000 in /tmp/tmp.qsomtrJz1H/Auth-Server-LB

Creating Credentials ...

Credentials in ~/.yar.creds
API_KEY=bd95fc48d57a4034939f04ef56fac46d
MAC_KEY_IDENTIFIER=4b480f4f9a2343089b9f8cbe534cb522
MAC_KEY=iPBKxnbbylBFUOK4qS-gS8ak7bQRyA4aVyey_e944XE
MAC_ALGORITHM=hmac-sha-1
vagrant@precise64:/vagrant$
~~~~~

* so what did ./spin_up_deployment.sh just do? it spun up a
highly simplified but complete deployment of yar
* you can see all the running services using docker's ps command

~~~~~
vagrant@precise64:/vagrant$ sudo docker ps
CONTAINER ID        IMAGE                  COMMAND                CREATED              STATUS              PORTS               NAMES
5c1514791174        haproxy_img:latest     haproxy -f /haproxyc   About a minute ago   Up About a minute                       dreamy_wright
886ffd903d05        yar_img:latest         auth_server --log=in   About a minute ago   Up About a minute                       furious_fermat
e160d943acc3        yar_img:latest         key_server --log=inf   About a minute ago   Up About a minute                       grave_lovelace
de58bfa2ce11        couchdb_img:latest     /bin/sh -c couchdb     About a minute ago   Up About a minute   5984/tcp            focused_wozniak
494464ec2278        memcached_img:latest   /bin/sh -c memcached   About a minute ago   Up About a minute   11211/tcp           high_bohr
2ea0d8cd56ea        haproxy_img:latest     haproxy -f /haproxyc   About a minute ago   Up About a minute                       sleepy_brattain
bb9ac51a422c        yar_img:latest         app_server --log=inf   About a minute ago   Up About a minute                       mad_hawking
vagrant@precise64:/vagrant$
~~~~~

* spin_up_deployment.sh also 
provisioned keys for [Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
and [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02)
authentication
* you can issue requests to using
[cURL](http://en.wikipedia.org/wiki/CURL) and
[yarcurl](../bin/yarcurl) - go ahead, try it

~~~~~
vagrant@precise64:/vagrant$ curl -s -u bd95fc48d57a4034939f04ef56fac46d: http://172.17.0.8:8000 | jpp
{
    "auth": "YAR dave@example.com",
    "status": "ok",
    "when": "2014-03-15 13:22:04.410721"
}
vagrant@precise64:/vagrant$ yarcurl GET http://172.17.0.8:8000 | jpp
{
    "auth": "YAR dave@example.com",
    "status": "ok",
    "when": "2014-03-15 13:25:10.753733"
}
~~~~~

* above we issued request to the deployment using
[cURL](http://en.wikipedia.org/wiki/CURL) and
[yarcurl](../bin/yarcurl) but if
you want to get a sense of how yar performs under load you'll
want to issue repeated requests at various concurrency levels - a simple
way to get going down that path is to use
[Apache's ab](http://httpd.apache.org/docs/2.4/programs/ab.html) utility which
you'll find has already been installed for you - below
is an example of using ab to issue 10,000 requests to the deployment's
auth server 10 requests at a time

~~~~~
vagrant@precise64:/vagrant$ ab -c 10 -n 10000 -A bd95fc48d57a4034939f04ef56fac46d: http://172.17.0.8:8000/dave.html
This is ApacheBench, Version 2.3 <$Revision: 655654 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 172.17.0.8 (be patient)
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
Server Hostname:        172.17.0.8
Server Port:            8000

Document Path:          /dave.html
Document Length:        86 bytes

Concurrency Level:      10
Time taken for tests:   128.914 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      2880000 bytes
HTML transferred:       860000 bytes
Requests per second:    77.57 [#/sec] (mean)
Time per request:       128.914 [ms] (mean)
Time per request:       12.891 [ms] (mean, across all concurrent requests)
Transfer rate:          21.82 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       2
Processing:    30  129  24.4    125     255
Waiting:       30  128  24.4    125     255
Total:         30  129  24.4    125     255

Percentage of the requests served within a certain time (ms)
  50%    125
  66%    134
  75%    141
  80%    145
  90%    160
  95%    173
  98%    190
  99%    201
 100%    255 (longest request)
~~~~~

* running a single [Apache ab](http://httpd.apache.org/docs/2.4/programs/ab.html)
is fine for getting a quick sense of how the yar deployment is performing - a far
better understanding is possible with some
creative bash scripting and gnuplot
* [run_load_test.sh](run_load_test.sh) is a pretty sweet bash script that
automates the entire yar load testing process
* [run_load_test.sh](run_load_test.sh) spins up a new yar deployment (using
[spin_up_deployment.sh](spin_up_deployment.sh), issues 5,000 requests to the
deployment using [ab](http://httpd.apache.org/docs/2.4/programs/ab.html) and
produces some graphs using [gnuplot](http://www.gnuplot.info/) that describe how
the deployment performed when [ab](http://httpd.apache.org/docs/2.4/programs/ab.html)
was running
* [run_load_test.sh](run_load_test.sh) repeats the above at concurrency levels of 1, 5,
10, 25, 50, 75 & 100 and then puts all of the graphs in a single pdf summary report

~~~~~
vagrant@precise64:/vagrant$ ./run_load_test.sh

<<<cut a bunch of output that is really not that interesting>>>

Complete results in '/vagrant/test-results/2014-03-01-13-46'
Summary report '/vagrant/test-results/2014-03-01-13-46/test-results-summary.pdf'
~~~~~

* below is a example of the kind of graphs you'll find in the summary report
![](samples/sample-load-test-result-graph.png)
* [here's](samples/sample-load-test-summary-report.pdf) a sample of the summary report

Key Store Load Test
-------------------
* [key_store_load_test.sh](key_store_load_test.sh) is used to explore
  * how the size of the key store increases as the number of credentials increases
  * how the time to retrieve credentials is affected by the number of credentials
* just like the deployment load tests described above,
the load test is run in the docker container
host - [key_store_load_test.sh](key_store_load_test.sh)
runs directly on the [VirtualBox](https://www.virtualbox.org/)
and the key store runs in a [Docker](https://www.docker.io/) container
* :TODO: add details on how to run the key store load test

![](samples/sample-key-store-size-graph.png)

* [here's](samples/sample-key-store-summary-report.pdf) a sample of the summary report

Other Stuff
-----------
* if at any point you need to remove all
containers so you can start from scratch just run [rm_all_containers.sh](rm_all_containers.sh) - just
be warned, [rm_all_containers.sh](rm_all_containers.sh) kills **all** running containers and
removes **all** file systems for all containers - note the emphasis on **all** -> 
if you're running yar containers right beside non-yar containers
[rm_all_containers.sh](rm_all_containers.sh) will remove the non-year containers
and file systems just as quickly and forcefully as it removes yar containers and file systems
* why are bash scripts used for lots of this testing? why not use Python
and [docker-py](https://github.com/dotcloud/docker-py)?
tried [docker-py](https://github.com/dotcloud/docker-py) but found the API to be poorly documented
and not used extensively (so Googling for answers yielded few hits).
The [Docker cli](http://docs.docker.io/en/latest/reference/commandline/cli/)
on the other hand is very well documented and lots of folks
are using it so easy to Google for answers.
