import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

import httpx
from httpx import Response

import logging

ENVIRON_WHITELIST = [
    "LD_LIBRARY_PATH", "LC_CTYPE", "LC_ALL", "PATH", "JAVA_HOME", "PYTHONPATH",
    "TS_CONFIG_FILE", "LOG_LOCATION", "METRICS_LOCATION",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"
]

log = logging.getLogger(__name__)


class LocalTS:
    def __init__(self,
                 model_store: str,
                 config_path: Optional[str] = None,
                 log_location: Optional[str] = None,
                 metrics_location: Optional[str] = None,
                 log_config: Optional[str] = None) -> None:
        new_env = {}
        env = os.environ
        for x in ENVIRON_WHITELIST:
            if x in env:
                new_env[x] = env[x]
        if config_path:
            new_env["TS_CONFIG_FILE"] = config_path
        if log_location:
            new_env["LOG_LOCATION"] = log_location
            if not os.path.isdir(log_location):
                os.makedirs(log_location, exist_ok=True)
        if metrics_location:
            new_env["METRICS_LOCATION"] = metrics_location
            if not os.path.isdir(metrics_location):
                os.makedirs(metrics_location, exist_ok=True)

        self.model_store = model_store
        self.config_path = config_path
        self.log_location = log_location
        self.metrics_location = metrics_location
        self.log_config = log_config
        self.env = new_env

    def check_version(self) -> Tuple[str, Union[str, Exception]]:
        try:
            p = subprocess.run(["torchserve", "--version"],
                               check=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
            return p.stdout, p.stderr
        except (subprocess.CalledProcessError, OSError) as e:
            return "", e

    def start_torchserve(self) -> str:

        if not os.path.exists(self.model_store):
            return "Can't find model store path"
        elif not os.path.exists(self.config_path):
            return "Can't find configuration path"
        dashboard_log_path = os.path.join(
            self.log_location, "torchserve_dashboard.log"
        ) if self.log_location is not None else None
        torchserve_cmd = f"torchserve --start --ncs --model-store {self.model_store} --ts-config {self.config_path}"
        if self.log_config:
            torchserve_cmd += f" --log-config {self.log_config}"
        p = subprocess.Popen(
            torchserve_cmd.split(" "),
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=open(dashboard_log_path, "a+")
            if dashboard_log_path else subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True  # IDK stackoverflow told me to do it
        )
        p.communicate()
        if p.returncode == 0:
            return f"Torchserve is starting (PID: {p.pid})..please refresh page"
        else:
            return f"Torchserve is already started. Check {dashboard_log_path} for errors"

    def stop_torchserve(self) -> Union[str, Exception]:
        try:
            p = subprocess.run(["torchserve", "--stop"],
                               check=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
            return p.stdout
        except (subprocess.CalledProcessError, OSError) as e:
            return e

    def get_model_store(self) -> List[str]:
        return os.listdir(self.model_store)


class ManagementAPI:
    def __init__(self, address: str, error_callback: Callable = None) -> None:
        self.address = address
        if not error_callback:
            error_callback=self.default_error_callback
        self.client = httpx.Client(timeout=1000,
                                   event_hooks={"response": [error_callback]})
    @staticmethod
    def default_error_callback(response: Response) -> None:
        if response.status_code != 200:
            log.info(f"Warn - status code: {response.status_code},{response}")

    def get_loaded_models(self) -> Optional[Dict[str, Any]]:
        try:
            res = self.client.get(self.address + "/models")
            return res.json()
        except httpx.HTTPError:
            return None

    def get_model(self,
                  model_name: str,
                  version: Optional[str] = None,
                  list_all: bool = False,
                  custom_metadata: bool = False) -> List[Dict[str, Any]]:
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        elif list_all:
            req_url += "/all"
        if custom_metadata:
            req_url += "?customized=true"

        res = self.client.get(req_url)
        return res.json()

    # Doesn't have version
    def register_model(
        self,
        mar_path: str,
        model_name: Optional[str] = None,
        handler: Optional[str] = None,
        runtime: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_batch_delay: Optional[int] = None,
        initial_workers: Optional[int] = None,
        response_timeout: Optional[int] = None,
        is_encrypted: Optional[bool] = None,
    ) -> Dict[str, str]:

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
        if is_encrypted:
            req_url += "&s3_sse_kms=true"

        res = self.client.post(req_url)
        return res.json()

    def delete_model(self,
                     model_name: str,
                     version: Optional[str] = None) -> Dict[str, str]:
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        res = self.client.delete(req_url)
        return res.json()

    def change_model_default(self,
                             model_name: str,
                             version: Optional[str] = None):
        req_url = self.address + "/models/" + model_name
        if version:
            req_url += "/" + version
        req_url += "/set-default"
        res = self.client.put(req_url)
        return res.json()

    def change_model_workers(
            self,
            model_name: str,
            version: Optional[str] = None,
            min_worker: Optional[int] = None,
            max_worker: Optional[int] = None,
            number_gpu: Optional[int] = None) -> Dict[str, str]:
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

    def register_workflow(self,
                          url: str,
                          workflow_name: Optional[str] = None) -> Dict[str, str]:
        req_url = self.address + "/workflows/" + url
        if workflow_name:
            req_url += "&workflow_name=" + workflow_name
        res = self.client.post(req_url)
        return res.json()

    def get_workflow(self, workflow_name: str) -> Dict[str, str]:
        req_url = self.address + "/workflows/" + workflow_name
        res = self.client.get(req_url)
        return res.json()

    def unregister_workflow(self, workflow_name: str) -> Dict[str, str]:
        req_url = self.address + "/workflows/" + workflow_name
        res = self.client.delete(req_url)
        return res.json()

    def list_workflows(
        self,
        limit: Optional[int] = None,
        next_page_token: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
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
