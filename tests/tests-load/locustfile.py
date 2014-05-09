#
# this module is a locustfile drives load into a yar deployment
#
# the command line below illusrates how this locustfile is typically
# expected to called from a BASH command line
#
#    locust \
#        -f ./locustfile.py \
#        -H http://172.17.0.8:8000 \
#        --no-web \
#        -n 10000 \
#        -c 25 \
#        -r 5 \
#        --logfile=./raw_data.tsv
#
# the locustfile is a pretty and simple locustfile except for
# a couple of things
#
#    1/ the locustfile assumes ~/.yar.creds.random.set exists
#    and contains a set of previously generated yar credentials
#
#    2/ Behavior.get_request() spins in a continuous loop issuing
#    one request to the yar deployment after another - with locust
#    you define a concurrency level and a set of user behaviors
#    encapsulated in a locust's class - every second locust looks
#    at the number of currently executing locusts and starts the
#    number needed to reach the specified concurrency levels - it
#    doesn't seem typical that locust classes loop forever but this
#    approach ensures the desired concurrency levels are maintained
#

import json
import os
import random
import time

from locust import HttpLocust
from locust import task
from locust import TaskSet
from requests.auth import AuthBase

import mac

with open(os.path.expanduser("~/.yar.creds.random.set"), "r") as f:
    _creds = [json.loads(line.strip()) for line in f]

class Behavior(TaskSet):
    min_wait = 0
    max_wait = 0

    @task
    def get_request(self):
        while True:
            client = self.client
            path = "/dave.html"
            creds = _creds[int(random.uniform(0, len(_creds) - 1))]
            auth = self._get_auth(creds)
            response = client.get(path, auth=auth) if auth else client.get(path)

            print "TO_GET_TAB_TO_WORK\t%d\t%s\tNOTHING_BY_DESIGN\t%d" % (
                int(time.time()),
                response.status_code,
                1000 * response.elapsed.total_seconds())

    def _get_auth(creds):
        if "api_key" in creds:
            auth = HTTPBasicAuth(creds["api_key"], "")
            return auth

        if "mac_key_identifier" in creds:
            auth = mac.RequestsAuth(
                mac.MACKeyIdentifier(creds["mac_key_identifier"]),
                mac.MACKey(creds["mac_key"]),
                creds["mac_algorithm"])
            return auth

        return None

class User(HttpLocust):
    task_set = Behavior
