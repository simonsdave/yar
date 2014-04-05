Testing and experimenting with a full yar deployment
is done by creating a series of
[Docker](https://www.docker.io/) containers to run
instances of the various yar services. The number, type
and size of these containers can be varied to validate
yar's operation in various deployment configurations.
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

Let's walk through this process step by step.
We'll assume you don't have the yar source code on your machine.

* let's start from scratch, assuming you don't even have the yar source code - first
we'll get the source code and pre-reqs by running the
following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git; cd yar; source bin/cfg4dev
~~~~~

* now let's get to the directory where we'll build the
[box](http://docs.vagrantup.com/v2/boxes.html)

~~~~~
(env)>cd tests/load/precise64-3.8-kernel
~~~~~

* use [Vagrant](http://www.vagrantup.com/) to provision
a [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
[box](http://docs.vagrantup.com/v2/boxes.html)
with version 3.8 of the Linux kernel

~~~~~
(env)>vagrant up
<<<lots of messages>>>
(env)>vagrant status
Current machine states:
default                   running (virtualbox)
~~~~~

* use [Vagrant](http://www.vagrantup.com/)'s
[package](https://docs.vagrantup.com/v2/cli/package.html)
command to create a
[box](http://docs.vagrantup.com/v2/boxes.html)
in the local directory

~~~~~
(env)>vagrant package --output precise64-3.8-kernel.box
==> default: Attempting graceful shutdown of VM...
==> default: Clearing any previously set forwarded ports...
==> default: Exporting VM...
==> default: Compressing package to: /Users/dave/yar/tests/load/precise64-3.8-kernel/precise64-3.8-kernel.box
~~~~~

* use [Vagrant](http://www.vagrantup.com/)'s
[box add](https://docs.vagrantup.com/v2/cli/box.html)
command to add the
[box](http://docs.vagrantup.com/v2/boxes.html)
to the local repo of boxes

> IMPORTANT - in the code below it's important to get the 
> [box](http://docs.vagrantup.com/v2/boxes.html)
> name *precise64-3.8-kernel* right because
> it's referred to by name in
> [this Vagrantfile](../docker-container-host/Vagrantfile.sh)

~~~~~
(env)>vagrant box add precise64-3.8-kernel precise64-3.8-kernel.box
==> box: Adding box 'precise64-3.8-kernel' (v0) for provider:
    box: Downloading: file:///Users/dave/yar/tests/load/precise64-3.8-kernel/precise64-3.8-kernel.box
==> box: Successfully added box 'precise64-3.8-kernel' (v0) for 'virtualbox'!
~~~~~

* we're done and to convince yourself of this 
use [Vagrant](http://www.vagrantup.com/)'s
[box list](https://docs.vagrantup.com/v2/cli/box.html)
to see the *precise64-3.8-kernel* 
[box](http://docs.vagrantup.com/v2/boxes.html)
in local box repo

~~~~~
(env)>vagrant box list
precise64            (virtualbox, 0)
precise64-3.8-kernel (virtualbox, 0)
(env)>
~~~~~
