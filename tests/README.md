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
[Mac OS X](http://www.apple.com/ca/osx/).
[Docker](https://www.docker.io/) doesn't support
[Mac OS X](http://www.apple.com/ca/osx/)
so a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/) is
used as the [Docker](https://www.docker.io/) container host.
See [these instructions](box-base-docker-container-host/README.md)
for all the details of the one time process to create
the docker container host. Once you have created the
[box](http://docs.vagrantup.com/v2/boxes.html)
you should see something like the following

~~~~~
(env)>vagrant box list
base-docker-container-host (virtualbox)
trusty                     (virtualbox)
(env)>
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

* let's spin up a minimal yar deployment

~~~~~
vagrant@vagrant-ubuntu-trusty-64:/vagrant$ ./spin_up_deployment.sh
Initalizating Deployment
-- Removing all existing containers
-- Removing '~/.yar.deployment'
-- Removing '~/.yar.creds'
-- Removing '~/.yar.creds.random.set'
-- Deployment Location '/tmp/tmp.XQQwX0r0Wr'
Starting App Service(s)
-- 1: Starting App Service
-- 1: App Service listening on 172.17.0.2:8080
Starting App Service LB
-- App Service LB listening on 172.17.0.3:8080
Starting Nonce Store(s)
-- 1: Starting Nonce Store
-- 1: Nonce Store listening on 172.17.0.4:11211
Starting Key Store
-- Key Store listening on 172.17.0.5:5984/creds
Starting Key Service(s)
-- 1: Starting Key Service
-- 1: Key Service listening on 172.17.0.6:8070
Starting Key Service LB
-- Key Service LB listening on 172.17.0.7:8070
Starting Auth Service(s)
-- 1: Starting Auth Service
-- Auth Service listening on 172.17.0.8:8000
Starting Auth Service LB
-- Auth Service LB listening on 172.17.0.9:8000
Deployment Highlights
-- entry point @ 172.17.0.9:8000
-- creds in ~/.yar.creds
-- description in ~/.yar.deployment
vagrant@vagrant-ubuntu-trusty-64:/vagrant$
~~~~~

* [spin_up_deployment.sh](spin_up_deployment.sh) just did a ton of work for us
* in the output above, take note of the "Deployment Highlights" section
which describes elements of the deployment
* let's walk thru each of items in the "Deployment Highlights" section
* "entry point" describes the IP + port pair of the HAProxy
instance that balances load across all auth services in the deployment
* let' issue a [cURL](http://en.wikipedia.org/wiki/CURL) command
to the entry point and see what happens

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

* the first [cURL](http://en.wikipedia.org/wiki/CURL)
request failed so we issued a section [cURL](http://en.wikipedia.org/wiki/CURL)
request with the -v option so we could get a better
sense of what was happening
* the HTTP response code was 401 Unauthorized
* why? the [cURL](http://en.wikipedia.org/wiki/CURL)
requests are getting rejected by the auth
servers because the auth services can't authenticate the request
which brings us to the second item the "Deployment Highlights" section
* as part of spinning up the deployment, [spin_up_deployment.sh](spin_up_deployment.sh)
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

* armed with the credentials let's issue a
new [cURL](http://en.wikipedia.org/wiki/CURL)
request that the auth services will be able to
successfully authenticate

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
* how that we've seen
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
working how about some
[MAC](http://en.wikipedia.org/wiki/Message_authentication_code)
authentication
* this time we'll use yarcurl to issue the request - yarcurl
will automagically pick up the required credentials from ~/.yar.creds,
calculate the required Authorization header and issue a
[cURL](http://en.wikipedia.org/wiki/CURL) request

~~~~~
vagrant@precise64:/vagrant$ yarcurl -v GET http://172.17.0.9:8000
* About to connect() to 172.17.0.9 port 8000 (#0)
*   Trying 172.17.0.9... connected
> GET / HTTP/1.1
> User-Agent: curl/7.22.0 (x86_64-pc-linux-gnu) libcurl/7.22.0 OpenSSL/1.0.1 zlib/1.2.3.4 libidn/1.23 librtmp/2.3
> Host: 172.17.0.9:8000
> Accept: */*
> Authorization: MAC id="b76066b21815448081645b9355a7dd93", ts="1399216364", nonce="21545e760586dfa7448181d465cf84ad", ext="", mac="fd6662158141f596919d63e63b51ea68b7f52695"
>
< HTTP/1.1 200 OK
< Content-Length: 86
< Connection: close
< Etag: "6079df79c941ff7afe0eec855e23d2eaea59f32f"
< Date: Sun, 04 May 2014 15:12:44 GMT
< Content-Type: application/json; charset=UTF-8
<
* Closing connection #0
{"status": "ok", "when": "2014-05-04 15:12:44.586694", "auth": "YAR dave@example.com"}vagrant@precise64:/vagrant$
~~~~~

* again, 200 OK = success! nice:-)

Next Steps
----------

The above barely scratched the surface on the features
of this testing infrastructure. Below are some suggestions
for next steps.

* rather than spinning up a single instance of each yar service,
take a look at [spin_up_deployment.sh's](spin_up_deployment.sh)
-p option to see how
to supply a deployment profile which describes the shape
of the deployment - also take a look at
[this](samples/sample-load-deployment-profile.json)
sample deployment profile
* building on the knowledge you've gain about
issuing [cURL](http://en.wikipedia.org/wiki/CURL)
requests with
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
to use [Apache's ab](http://httpd.apache.org/docs/2.4/programs/ab.html)
to start driving load into a deployment
* while you're driving load thru the
[HAProxy load balancers](http://haproxy.1wt.eu/)
it can be useful to look at the
[stats reporting](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#stats%20enable) - after a bunch of Vagrant and Docker detailed fussing
this was made possible - in a browser on the same machine running
your testing VM, go to the links below (in all cases
the user name is yar and password is yar):

  * [http://localhost:8000/auth_service_lb?stats](http://localhost:8000/auth_service_lb?stats) for auth service LB stats
  * [http://localhost:8070/key_service_lb?stats](http://localhost:8070/key_service_lb?stats) for key service LB stats
  * [http://localhost:8080/app_service_lb?stats](http://localhost:8080/app_service_lb?stats) for app service LB stats

* this entire testing infrastructure was initally built to enable
load testing - to explore load testing capabilities look at:

  * [full deployment load testing](tests-load)
  * [key store load testing](tests-key-store-size)

* if at any point you need to remove all
containers so you can start from scratch just run
[rm_all_containers.sh](rm_all_containers.sh)

FAQ
---
* why are bash scripts used for lots of this testing? why not use Python
and [docker-py](https://github.com/dotcloud/docker-py)?
tried [docker-py](https://github.com/dotcloud/docker-py) but found
the API to be poorly documented
and not used extensively (so Googling for answers yielded few hits).
The [Docker cli](http://docs.docker.io/en/latest/reference/commandline/cli/)
on the other hand is very well documented and lots of folks
are using it so easy to Google for answers.
