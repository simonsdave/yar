[These instructions](..) describe how to spin up a functionally
complete deployment of yar in a single VM. The remainder of this
page builds on those instructions and describes how to run a
load test on the VM.

Massively Quick Intro to Running A Load Test
--------------------------------------------
A ton of effort has gone into automating the load testing process
so the instructions for running a load test are actually really
simple. Instead of writing a long description of these
instructions just follow the commands in the terminal window below.

~~~~~
>cd; cd yar; source bin/cfg4dev; cd tests
(env)>./provision.sh
<<<cut lots of messages>>>
Cleaning up...
 ---> 296a0d185246
Successfully built 296a0d185246
Removing intermediate container 5a44c1ec3b91
<<<cut lots of messages>>>
Removing intermediate container d984d433d10b
(env)>vagrant ssh
Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.8.0-38-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Welcome to your Vagrant-built virtual machine.
Last login: Fri Sep 14 06:23:18 2012 from 10.0.2.2
vagrant@precise64:~$ cd /vagrant/tests-load/
vagrant@precise64:/vagrant/tests-load$ ./run_load_test.sh
5: Spinning up a deployment
5: Deployment end point = 172.17.0.9:8000
5: Using Apache Bench
5: Getting creds
5: Starting to drive load
5: Generating graphs
Complete results in '/vagrant/tests-load/test-results/2014-05-02-00-52'
Summary report '/vagrant/tests-load/test-results/2014-05-02-00-52/test-results-summary.pdf'
vagrant@precise64:/vagrant/tests-load$
~~~~~

* below is a example of the kind of graphs you'll find in the
load test's summary report and
[here's](samples/sample-load-test-summary-report.pdf) a sample
of the full summary report
![](samples/sample-load-test-result-graph.png)

Next Steps
----------
* take a look at [run_load_test.sh's](run_load_test.sh)
-p option to see how to supply a test profile which
describes the shape of the deployment to load test
along with various load testing parameters - also take
a look at [this](samples/sample-load-test-profile.json)
sample test profile which explains the various test
parameters
