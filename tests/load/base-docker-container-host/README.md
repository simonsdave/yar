Creating a base Docker Container Host
[box](http://docs.vagrantup.com/v2/boxes.html)
is simple. Let's start from scratch assuming
you don't even have the yar source code.

* first we'll get the source code and pre-reqs
by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git; cd yar; source bin/cfg4dev
~~~~~

* now let's get to the directory where we'll build the
[box](http://docs.vagrantup.com/v2/boxes.html)

~~~~~
(env)>cd tests/load/base-docker-container-host
~~~~~

* use [Vagrant](http://www.vagrantup.com/) to spin up
the [VirtualBox](https://www.virtualbox.org/)
[box](http://docs.vagrantup.com/v2/boxes.html)
that will become the base Docker Container Host

> NOTE - if you get an error talking about a missing
> box called *precise64-3.8-kernel* it just means
> you have to run through the steps described
> [here](../precise64-3.8-kernel/README.md)

~~~~~
(env)>vagrant up
<<<lots of messages>>>
Processing triggers for libc-bin ...
ldconfig deferred processing now taking place
(env)>vagrant status
Current machine states:
default                   running (virtualbox)

The VM is running. To stop this VM, you can run `vagrant halt` to
shut it down forcefully, or you can run `vagrant suspend` to simply
suspend the virtual machine. In either case, to restart it again,
simply run `vagrant up`.
~~~~~

* use [Vagrant](http://www.vagrantup.com/)'s
[package](https://docs.vagrantup.com/v2/cli/package.html)
command to create a
[box](http://docs.vagrantup.com/v2/boxes.html)
in the local directory

~~~~~
(env)>vagrant package --output base-docker-container-host.box
==> default: Attempting graceful shutdown of VM...
==> default: Clearing any previously set forwarded ports...
==> default: Exporting VM...
==> default: Compressing package to: /Users/dave/yar/tests/load/base-docker-container-host/base-docker-container-host.box
(env)>
~~~~~

* use [Vagrant](http://www.vagrantup.com/)'s
[box add](https://docs.vagrantup.com/v2/cli/box.html)
command to add the
[box](http://docs.vagrantup.com/v2/boxes.html)
to the local repo of boxes

> IMPORTANT - in the code below it's important to get the 
> [box](http://docs.vagrantup.com/v2/boxes.html)
> name *base-docker-container-host* right because
> it's referred to by name in
> [this Vagrantfile](../Vagrantfile)

~~~~~
(env)>vagrant box add base-docker-container-host base-docker-container-host.box
==> box: Adding box 'base-docker-container-host' (v0) for provider:
    box: Downloading: file:///Users/dave/yar/tests/load/base-docker-container-host/base-docker-container-host.box
==> box: Successfully added box 'base-docker-container-host' (v0) for 'virtualbox'!
(env)>
~~~~~

* we're done and to convince yourself of this
use [Vagrant](http://www.vagrantup.com/)'s
[box list](https://docs.vagrantup.com/v2/cli/box.html)
to see the *base-docker-container-host*
[box](http://docs.vagrantup.com/v2/boxes.html)
in local box repo

~~~~~
(env)>vagrant box list
base-docker-container-host (virtualbox, 0)
precise64                  (virtualbox, 0)
precise64-3.8-kernel       (virtualbox, 0)
(env)>
~~~~~
