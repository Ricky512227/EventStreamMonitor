from flask import Flask


class CreatFlaskApp:
    def __init__(self, service_name):
        self.service_name = service_name
        self.app_name = None


    def create_app_instance(self):
        print("Received Service [{0}]".format(self.service_name))
        app_name = Flask(self.service_name)
        print("Flask of Application Instance created for service [{0}] ,  App Name :: [{1}] ==> SUCCESS".format(self.service_name, app_name))
        return app_name




