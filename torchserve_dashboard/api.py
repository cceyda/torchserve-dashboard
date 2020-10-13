import os
import subprocess

import httpx

import streamlit as st

def raise_on_not200(response):
    if response.status_code != 200:
        st.write("There was an error!")
        st.write(response)


client = httpx.Client(timeout=1000, event_hooks={"response": [raise_on_not200]})


def start_torchserve(model_store, config_path):
    if os.path.exists(model_store) and os.path.exists(config_path):
        torchserve_cmd = f"torchserve --start --ncs --model-store {model_store} --ts-config {config_path}"
        subprocess.Popen(
            torchserve_cmd.split(" "),
            stdout=open("/dev/null", "w"),
            stderr=open("/dev/null", "w"),
            preexec_fn=os.setpgrp,
        )
        return "Torchserve is starting..please refresh page"


def stop_torchserve():
    subprocess.Popen(["torchserve", "--stop"])
    return "Torchserve stopped"


def get_loaded_models(M_API):
    try:
        res = client.get(M_API + "/models")
        return res.json()
    except httpx.HTTPError as exc:
        return None


def get_model(M_API, model_name, version=None, list_all=False):
    req_url = M_API + "/models/" + model_name
    if version:
        req_url += "/" + version
    elif list_all:
        req_url += "/all"

    res = client.get(req_url)
    return res.json()


def register_model(
    M_API,
    mar_path,
    model_name=None,
    version=None,
    handler=None,
    runtime=None,
    batch_size=None,
    max_batch_delay=None,
    initial_workers=None,
    response_timeout=None,
):

    req_url = M_API + "/models?url=" + mar_path + "&synchronous=false"
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

    res = client.post(req_url)
    return res.json()


def delete_model(M_API, model_name, version):
    req_url = M_API + "/models/" + model_name
    if version:
        req_url += "/" + version
    res = client.delete(req_url)
    return res.json()


def change_model_default(M_API, model_name, version):
    req_url = M_API + "/models/" + model_name
    if version:
        req_url += "/" + version
    req_url += "/set-default"
    res = client.put(req_url)
    return res.json()
