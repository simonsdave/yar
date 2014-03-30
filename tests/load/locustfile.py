from locust import HttpLocust
from locust import TaskSet
from requests.auth import HTTPBasicAuth

# locust -f ./locustfile.py -H http://172.17.0.9:8000 --no-web -n 100 -c 10 --logfile=./ooo

class Behavior(TaskSet):
    def on_start(self):
        response = self.client.get(
            "/dave-was-here.html",
            auth=HTTPBasicAuth("8ca21f9dd6ea404d912a518263bc2b58", ""))
        print ">>>%s<<<>>>%s<<<" % (response.status_code, response.elapsed.total_seconds())


class User(HttpLocust):
    task_set = Behavior
    min_wait = 0
    max_wait = 0
