import os
import subprocess

import httpx

import logging

ENVIRON_WHITELIST = ["LD_LIBRARY_PATH", "LC_CTYPE", "LC_ALL", "PATH", "JAVA_HOME", "PYTHONPATH", "TS_CONFIG_FILE", "LOG_LOCATION", "METRICS_LOCATION"]

log = logging.getLogger(__name__)


class LocalTS:
    def __init__(self, model_store, config_path, log_location=None, metrics_location=None):
        new_env = {}
        env = os.environ
        for x in ENVIRON_WHITELIST:
            if x in env:
                new_env[x] = env[x]
        if log_location:
            new_env["LOG_LOCATION"] = log_location
        if metrics_location:
            new_env["METRICS_LOCATION"] = metrics_location
        if not os.path.isdir(metrics_location):
            os.makedirs(metrics_location, exist_ok=True)
        if not os.path.isdir(log_location):
            os.makedirs(log_location, exist_ok=True)

        self.model_store = model_store
        self.config_path = config_path
        self.log_location = log_location
        self.metrics_location = metrics_location
        self.env = new_env
    
    def check_version(self):
        try:
            p=subprocess.run(["torchserve","--version"], check=True,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            universal_newlines=True)
            return p.stdout ,p.stderr
        except (subprocess.CalledProcessError,OSError) as e:
            return "",e
         
    def start_torchserve(self):

        if not os.path.exists(self.model_store):
            return "Can't find model store path"
        elif not os.path.exists(self.config_path):
            return "Can't find configuration path"
        dashboard_log_path = os.path.join(self.log_location, "torchserve_dashboard.log")
        torchserve_cmd = f"torchserve --start --ncs --model-store {self.model_store} --ts-config {self.config_path}"
        p = subprocess.Popen(
            torchserve_cmd.split(" "),
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=open(dashboard_log_path, "a+"),
            start_new_session=True,
            close_fds=True  # IDK stackoverflow told me to do it
        )
        p.communicate()
        if p.returncode == 0:
            return f"Torchserve is starting (PID: {p.pid})..please refresh page"
        else:
            return f"Torchserve is already started. Check {dashboard_log_path} for errors"

    def stop_torchserve(self):
        try:
            p=subprocess.run(["torchserve","--stop"], check=True,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            universal_newlines=True)
            return p.stdout
        except (subprocess.CalledProcessError,OSError) as e:
            return e

class ManagementAPI:

    def __init__(self, address, error_callback):
        self.address = address
        self.client = httpx.Client(timeout=1000, event_hooks={"response": [error_callback]})

    def default_error_callback(response):
        if response.status_code != 200:
            log.info(f"Warn - status code: {response.status_code},{response}")

    def get_loaded_models(self):
        try:
            res = self.client.get(self.address + "/models")
            return res.json()
        except httpx.HTTPError:
            return None

    def get_model(self, model_name, version=None, list_all=False):
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        elif list_all:
            req_url += "/all"

        res = self.client.get(req_url)
        return res.json()

    # Doesn't have version
    def register_model(
        self,
        mar_path,
        model_name=None,
        handler=None,
        runtime=None,
        batch_size=None,
        max_batch_delay=None,
        initial_workers=None,
        response_timeout=None,
    ):

        req_url = self.address + "/models?url=" + mar_path + "&synchronous=false"
        if model_name:
            req_url += "&model_name=" + model_name
        if handler:
            req_url += "&handler=" + handler
        if runtime:
            req_url += "&runtime=" + runtime
        if batch_size:
            req_url += "&batch_size=" + str(batch_size)
        if max_batch_delay:
            req_url += "&max_batch_delay=" + str(max_batch_delay)
        if initial_workers:
            req_url += "&initial_workers=" + str(initial_workers)
        if response_timeout:
            req_url += "&response_timeout=" + str(response_timeout)

        res = self.client.post(req_url)
        return res.json()

    def delete_model(self, model_name, version):
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        res = self.client.delete(req_url)
        return res.json()

    def change_model_default(self, model_name, version):
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        req_url += "/set-default"
        res = self.client.put(req_url)
        return res.json()

    def change_model_workers(self, model_name, version=None, min_worker=None, max_worker=None, number_gpu=None):
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        req_url += "?synchronous=false"
        if min_worker:
            req_url += "&min_worker=" + str(min_worker)
        if max_worker:
            req_url += "&max_worker=" + str(max_worker)
        if number_gpu:
            req_url += "&number_gpu=" + str(number_gpu)
        res = self.client.put(req_url)
        return res.json()

    def register_workflow(
        self,
        url,
        workflow_name=None
    ):
        req_url = self.address + "/workflows/" + url
        if workflow_name:
            req_url += "&workflow_name=" + workflow_name
        res = self.client.post(req_url)
        return res.json()

    def get_workflow(self, workflow_name):
        req_url = self.address + "/workflows/" + workflow_name
        res = self.client.get(req_url)
        return res.json()

    def unregister_workflow(self, workflow_name):
        req_url = self.address + "/workflows/" + workflow_name
        res = self.client.delete(req_url)
        return res.json()

    def list_workflows(self, limit=None, next_page_token=None):
        req_url = self.address + "/workflows/"
        if limit:
            req_url += "&limit=" + str(limit)
        if next_page_token:
            req_url += "&next_page_token=" + str(next_page_token)
        try:
            res = self.client.get(req_url)
        except httpx.HTTPError:
            return None
        return res.json()
