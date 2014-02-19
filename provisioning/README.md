yar integration testing is done by creating a series of
[Docker](https://www.docker.io/) containers to run
instances of the various yar services. The number, type
and size of these containers can be varied to validate
yar's operation in various deployment configurations.

The target deployment OS for yar is
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
and therefore the Docker containers run this same OS.

The development environment for yar has been and
continues to be Mac OS X. Docker support for Mac OS X
is limited and thus a far better supported Docker container
host is required. [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)
was selected as the container host for integration testing.
[Vagrant](http://www.vagrantup.com/) is used to spin a
[Ubuntu 12.04](http://releases.ubuntu.com/12.04/) virtual machine
on [VirtualBox](https://www.virtualbox.org/) and
this virtual machine acts as the container host.
