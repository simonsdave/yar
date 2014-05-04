Testing against and experimenting with a full yar deployment
is done by creating a series of
[Docker](https://www.docker.io/) containers which run
instances of the various yar services. The number, type
and size of these containers can be varied when the deployment
is spun up to validate yar's operation in a variety of
deployment configurations. Also, after an initial deployment
is up and running, it is also possible to add and remove
service instances to explore, understand and verify key
operational scenarios.

The primary development environment for yar is
[Mac OS X](http://www.apple.com/ca/osx/)
and the intended deployment environment is 
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/).
[Docker](https://www.docker.io/) doesn't support
[Mac OS X](http://www.apple.com/ca/osx/)
so a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 12.04](http://releases.ubuntu.com/12.04/) is
used as the [Docker](https://www.docker.io/) container host. 

* use [Vagrant](http://www.vagrantup.com/) to create
a [VirtualBox](https://www.virtualbox.org/)
[box](http://docs.vagrantup.com/v2/boxes.html)
running [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and version 3.8 of the Linux kernel - see
[these instructions](precise64-3.8-kernel/README.md) for all the details - note
this is a one time operation and is only required because the updated
kernel version is required by [Docker](https://www.docker.io/)
* again using [Vagrant](http://www.vagrantup.com/),
build on the [box](http://docs.vagrantup.com/v2/boxes.html)
just created and create a second [box](http://docs.vagrantup.com/v2/boxes.html)
provisioned with all the base [Docker](https://www.docker.io/)
images, infrastructure and test tools that are needed to spin
up and test a yar deployment - see [these instructions](base-docker-container-host/README.md)
for all the details - note, like creating the previous
[box](http://docs.vagrantup.com/v2/boxes.html), creating this [box](http://docs.vagrantup.com/v2/boxes.html)
is a one time operation
* once you have created the above [boxes](http://docs.vagrantup.com/v2/boxes.html)
you should see something like the following

~~~~~
(env)>vagrant box list
base-docker-container-host (virtualbox, 0)
precise64                  (virtualbox, 0)
precise64-3.8-kernel       (virtualbox, 0)
~~~~~

* now it's time to use [Vagrant](http://www.vagrantup.com/)
to spin up a [VirtualBox](https://www.virtualbox.org/) VM

~~~~~
cd; cd yar; source bin/cfg4dev; cd tests; ./provision.sh
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

* once the VM is running, ssh into it

~~~~~
(env)>vagrant ssh
Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.8.0-38-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Welcome to your Vagrant-built virtual machine.
Last login: Fri Sep 14 06:23:18 2012 from 10.0.2.2
vagrant@precise64:~$
~~~~~

* now let's get to the directory in the VM with all of the testing
tools and utilities

~~~~~
vagrant@precise64:~$ cd /vagrant
vagrant@precise64:~$ ls -l
vagrant@precise64:/vagrant$ ls -l
total 84
drwxr-xr-x 1 vagrant vagrant   136 May  4 14:26 artifacts
drwxr-xr-x 1 vagrant vagrant   306 May  3 13:08 box-base-docker-container-host
drwxr-xr-x 1 vagrant vagrant   170 May  3 12:32 box-precise64-3.8-kernel
drwxr-xr-x 1 vagrant vagrant   204 May  3 12:32 cfg-collectd
drwxr-xr-x 1 vagrant vagrant   170 May  3 12:32 cfg-haproxy
drwxr-xr-x 1 vagrant vagrant   238 May  4 12:34 lots-of-creds
-rw-r--r-- 1 vagrant vagrant   282 May  3 12:32 provision_post_vagrant_up.sh
-rwxr-xr-x 1 vagrant vagrant   642 May  3 12:32 provision.sh
-rw-r--r-- 1 vagrant vagrant 14140 May  3 12:32 README.md
-rwxr-xr-x 1 vagrant vagrant   536 May  3 12:32 rm_all_containers.sh
-rwxr-xr-x 1 vagrant vagrant  7291 May  3 12:32 spin_up_deployment.sh
drwxr-xr-x 1 vagrant vagrant   238 May  3 21:32 tests-key-store-size
drwxr-xr-x 1 vagrant vagrant   306 May  3 12:32 tests-load
-rw-r--r-- 1 vagrant vagrant 40705 May  3 15:11 util.sh
-rw-r--r-- 1 vagrant vagrant   493 May  3 12:32 Vagrantfile
drwxr-xr-x 1 vagrant vagrant   136 May  4 14:26 yar
-rwxr-xr-x 1 vagrant vagrant  2364 May  3 12:32 yar.sh
vagrant@precise64:~$
~~~~~

* let's spin up a really simple yar deployment

~~~~~
vagrant@precise64:/vagrant$ ./spin_up_deployment.sh
Initalizating Deployment
-- Removing all existing containers
-- Removing '~/.yar.deployment'
-- Removing '~/.yar.creds'
-- Removing '~/.yar.creds.random'
-- Deployment Location '/tmp/tmp.igS9ZsfsSK'
Starting App Server(s)
-- 1: Starting App Server
-- 1: App Server listening on 172.17.0.2:8080
Starting App Server LB
-- App Server LB listening on 172.17.0.3:8080
Starting Nonce Store(s)
-- 1: Starting Nonce Store
-- 1: Nonce Store listening on 172.17.0.4:11211
Starting Key Store
-- Key Store listening on 172.17.0.5:5984/creds
Starting Key Server(s)
-- 1: Starting Key Server
-- 1: Key Server listening on 172.17.0.6:8070
Starting Key Server LB
-- Key Server LB listening on 172.17.0.7:8070
Starting Auth Server(s)
-- 1: Starting Auth Server
-- Auth Server listening on 172.17.0.8:8000
Starting Auth Server LB
-- Auth Server LB listening on 172.17.0.9:8000
Deployment Highlights
-- entry point @ 172.17.0.9:8000
-- creds in ~/.yar.creds
-- description in ~/.yar.deployment
vagrant@precise64:/vagrant$
~~~~~

* spin_up_deployment.sh just did a **ton** of work for us
* in the output above you'll notice the highlights
described in the "Deployment Highlights" section
* let's walk thru each of items in "Deployment Highlights" section
* entry point describes the IP + port pair of the HAProxy
instances that balances load across all auth servers in
the deployment
* let' issue a cURL command to the entry point and see what happens

~~~~~
vagrant@precise64:/vagrant$ curl http://172.17.0.9:8000
vagrant@precise64:/vagrant$ curl -v http://172.17.0.9:8000
* About to connect() to 172.17.0.9 port 8000 (#0)
*   Trying 172.17.0.9... connected
> GET / HTTP/1.1
> User-Agent: curl/7.22.0 (x86_64-pc-linux-gnu) libcurl/7.22.0 OpenSSL/1.0.1 zlib/1.2.3.4 libidn/1.23 librtmp/2.3
> Host: 172.17.0.9:8000
> Accept: */*
>
< HTTP/1.1 401 Unauthorized
< Date: Sun, 04 May 2014 14:57:24 GMT
< Content-Length: 0
< Content-Type: text/html; charset=UTF-8
< Connection: close
<
* Closing connection #0
vagrant@precise64:/vagrant$
~~~~~

* the first cURL request failed so we issued a section cURL
request, this time with the -v command so we could get a better
sense of what was happening
* the HTTP response code was 401 Unauthorized
* why? the cURL requests are getting rejected by the auth
servers because the auth servers can't authenticate the request
which brings us to the second item the "Deployment Highlights" section
* as part of spinning up the deployment, spin_up_deployment.sh
provisioned some credentials and saved them in ~/.yar.creds
* let's take a look at ~/.yar.creds

~~~~~
vagrant@precise64:/vagrant$ cat ~/.yar.creds
API_KEY=5f4149f8057a4903af1805e74c2e1d20
MAC_KEY_IDENTIFIER=b76066b21815448081645b9355a7dd93
MAC_KEY=EM92Jdqi6zTuakxr6D3GLi2hO37lCitYs69ZGghJE7g
MAC_ALGORITHM=hmac-sha-1
vagrant@precise64:/vagrant$
~~~~~

* armed with the credentials let's issue a new cURL request

~~~~~
vagrant@precise64:/vagrant$ curl -v -u 5f4149f8057a4903af1805e74c2e1d20: http://172.17.0.9:8000
* About to connect() to 172.17.0.9 port 8000 (#0)
*   Trying 172.17.0.9... connected
* Server auth using Basic with user '5f4149f8057a4903af1805e74c2e1d20'
> GET / HTTP/1.1
> Authorization: Basic NWY0MTQ5ZjgwNTdhNDkwM2FmMTgwNWU3NGMyZTFkMjA6
> User-Agent: curl/7.22.0 (x86_64-pc-linux-gnu) libcurl/7.22.0 OpenSSL/1.0.1 zlib/1.2.3.4 libidn/1.23 librtmp/2.3
> Host: 172.17.0.9:8000
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Length: 86
< Connection: close
< Etag: "0d6eb733c05b376dafdbba2b426c1ea167ef37a6"
< Date: Sun, 04 May 2014 15:04:33 GMT
< Content-Type: application/json; charset=UTF-8
<
* Closing connection #0
{"status": "ok", "when": "2014-05-04 15:04:33.412551", "auth": "YAR dave@example.com"}
vagrant@precise64:/vagrant$
~~~~~

* 200 OK = success! nice:-)


~~~~~
vagrant@precise64:/vagrant$ sudo docker ps
CONTAINER ID        IMAGE                  COMMAND                CREATED              STATUS              PORTS                    NAMES
d11a5720bb35        haproxy_img:latest     haproxy.sh /haproxy/   About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp   Auth_Server_LB
f2bf69b25b59        yar_img:latest         auth_server --log=in   About a minute ago   Up About a minute                            Auth_Server_1
310b12f3c4c3        haproxy_img:latest     haproxy.sh /haproxy/   About a minute ago   Up About a minute   0.0.0.0:8070->8070/tcp   Key_Server_LB
f4caf2eec173        yar_img:latest         key_server --log=inf   About a minute ago   Up About a minute                            Key_Server_1
73f231179e1a        couchdb_img:latest     /bin/sh -c couchdb     About a minute ago   Up About a minute   5984/tcp                 Key_Store
13b630bc3a77        memcached_img:latest   memcached.sh 11211 1   About a minute ago   Up About a minute                            Nonce_Store_1
6de3b8af3185        haproxy_img:latest     haproxy.sh /haproxy/   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp   App_Server_LB
a39916a7f1a7        yar_img:latest         app_server --log=inf   About a minute ago   Up About a minute                            App_Server_1
~~~~~

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
