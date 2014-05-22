Creating a base Docker Container Host
[box](http://docs.vagrantup.com/v2/boxes.html)
is simple. Let's start from scratch assuming
you don't even have the yar source code.

* get the source code and pre-reqs
by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git; cd yar; source bin/cfg4dev
~~~~~

* get to the directory where we'll build the
[box](http://docs.vagrantup.com/v2/boxes.html)

~~~~~
(env)>cd tests/load/base-docker-container-host
~~~~~

* now the [create_box](create_box) script will do
all the grunt work for us

~~~~~
(env)>./create_box
<<<lots of messages>>>
.
.
.
~~~~~

* that's all there is to it and to convince yourself of this
use [Vagrant](http://www.vagrantup.com/)'s
[box list](https://docs.vagrantup.com/v2/cli/box.html)
to see the *base-docker-container-host*
[box](http://docs.vagrantup.com/v2/boxes.html)
in local box repo

~~~~~
(env)>vagrant box list
base-docker-container-host (virtualbox)
trusty                     (virtualbox)
(env)>
~~~~~
