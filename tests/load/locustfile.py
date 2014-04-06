#
# this module is a locustfile drives load into a yar deployment
#
# the command line below illusrates how this locustfile is typically
# expected to called from a BASH command line
#
#	locust \
#		-f ./locustfile.py \
#		-H http://172.17.0.8:8000 \
#		--no-web \
#		-n 10000 \
#		-c 25 \
#		-r 5 \
#		--logfile=./raw_data.tsv
#
# the locustfile is a pretty and simple locustfile except for
# a couple of things
#
#	1/ the locustfile assumes ~/.yar.creds.random.set exists
#	and contains a set of previously generated yar credentials
#
#	2/ Behavior.get_request() spins in a continuous loop issuing
#	one request to the yar deployment after another - with locust
#	you define a concurrency level and a set of user behaviors
#	encapsulated in a locust's class - every second locust looks
#	at the number of currently executing locusts and starts the
#	number needed to reach the specified concurrency levels - it
#	doesn't seem typical that locust classes loop forever but this
#	approach ensures the desired concurrency levels are maintained
#

import os
import random
import time

from locust import HttpLocust
from locust import task
from locust import TaskSet
from requests.auth import HTTPBasicAuth

with open(os.path.expanduser("~/.yar.creds.random.set"), "r") as f:
    _api_keys = [line.strip() for line in f]


class Behavior(TaskSet):
    min_wait = 0
    max_wait = 0

    @task
    def get_request(self):
		while True:
			api_key = _api_keys[int(random.uniform(0, len(_api_keys) - 1))]
			response = self.client.get(
				"/dave.html",
				auth=HTTPBasicAuth(api_key, ""))
			print "TO_GET_TAB_TO_WORK\t%d\t%s\tNOTHING_BY_DESIGN\t%d" % (
				int(time.time()),
				response.status_code,
				1000 * response.elapsed.total_seconds())


class User(HttpLocust):
    task_set = Behavior
