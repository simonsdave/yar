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
