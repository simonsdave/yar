from locust import HttpLocust
from locust import task
from locust import TaskSet
from requests.auth import HTTPBasicAuth

# locust -f ./locustfile.py -H http://172.17.0.8:8000 --no-web -n 10000 -c 25 -r 5 --logfile=./ooo

class Behavior(TaskSet):
    min_wait = 0
    max_wait = 0

    @task
    def get_request(self):
        response = self.client.get(
            "/dave-was-here.html",
            auth=HTTPBasicAuth("b2b3125dd6964307810cdcf27764aad0", ""))
        print ">>>%s<<<>>>%s<<<" % (response.status_code, response.elapsed.total_seconds())


class User(HttpLocust):
    task_set = Behavior
