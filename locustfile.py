from locust import HttpUser, task, between

class QuickstartUser(HttpUser):

    '''def on_start(self):
        self.client.post("/login", json={"username":"foo", "password":"bar"})
'''
    @task
    def hello_world(self):
        self.client.get("/")
        self.client.get("/api/items")