import time

from locust import HttpLocust
from locust import task
from locust import TaskSet
from requests.auth import HTTPBasicAuth

# locust -f ./locustfile.py -H http://172.17.0.8:8000 --no-web -n 10000 -c 25 -r 5 --logfile=./ooo

_start_time = time.time()

class Behavior(TaskSet):
    min_wait = 0
    max_wait = 0

    @task
    def get_request(self):
        response = self.client.get(
            "/dave-was-here.html",
            auth=HTTPBasicAuth("753786be2dda4da6b4ea13d5029ddfcc", ""))
        print "<<<%s>>>>>>%s<<<>>>%s<<<" % (
			int(round(time.time() - _start_time)),
			response.status_code,
			response.elapsed.total_seconds())


class User(HttpLocust):
    task_set = Behavior
