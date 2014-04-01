# locust -f ./locustfile.py -H http://172.17.0.8:8000 --no-web -n 10000 -c 25 -r 5 --logfile=./ooo

import os
import random
import time

from locust import HttpLocust
from locust import task
from locust import TaskSet
from requests.auth import HTTPBasicAuth

with open(os.path.expanduser("~/.yar.creds.random.set"), "r") as f:
    _api_keys = [line.strip() for line in f]

_start_time = time.time()


class Behavior(TaskSet):
    min_wait = 0
    max_wait = 0

    @task
    def get_request(self):
        api_key = _api_keys[int(random.uniform(0, len(_api_keys) - 1))]
        response = self.client.get(
            "/dave-was-here.html",
            auth=HTTPBasicAuth(api_key, ""))
        print "<<<%s>>>>>>%s<<<>>>%s<<<" % (
            int(round(time.time() - _start_time)),
            response.status_code,
            response.elapsed.total_seconds())


class User(HttpLocust):
    task_set = Behavior
