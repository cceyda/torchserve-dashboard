import argparse
import os

import streamlit as st
from streamlit.script_request_queue import RerunData
from streamlit.script_runner import RerunException

import api as tsa
from pathlib import Path

st.set_page_config(
    page_title="Torchserve Management Dashboard",
    page_icon="./icon.png",
    layout="centered",
    initial_sidebar_state="expanded",
)

parser = argparse.ArgumentParser(description="Torchserve dashboard")

parser.add_argument("--model_store", default=None, help="Directory where your models are stored")
parser.add_argument("--config_path", default="./default.torchserve.properties", help="Torchserve config path")
parser.add_argument("--log_location", default="./", help="Passed as environment variable LOG_LOCATION to Torchserve")
parser.add_argument("--metrics_location", default="./", help="Passed as environment variable METRICS_LOCATION to Torchserve")
try:
    args = parser.parse_args()
except SystemExit as e:
    os._exit(e.code)

st.title("Torchserve Management Dashboard")

M_API = "http://127.0.0.1:8081"
model_store = args.model_store
config_path = args.config_path
log_location = args.log_location
if log_location:
    log_location = str(Path(log_location).resolve())
metrics_location = args.metrics_location
if metrics_location:
    metrics_location = str(Path(metrics_location).resolve())
config = None
default_key = "None"

if os.path.exists(args.config_path):
    config = open(args.config_path, "r").readlines()
    for c in config:
        if c.startswith("model_store"):
            if not model_store:
                model_store = c.split("=")[-1].strip()
        if c.startswith("management_address"):
            M_API = c.split("=")[-1].strip()

if model_store is None:
    st.write("model_store is required!")


def rerun():
    raise RerunException(RerunData(None))


@st.cache(allow_output_mutation=True)
def last_res():
    return ["Nothing"]


def get_model_store():
    return os.listdir(model_store)

# As a design choice I'm leaving config_path,log_location,metrics_location non-editable from the UI as a semi-security measure (maybe?:/)
##########Sidebar##########
st.sidebar.markdown(f"## Help")
with st.sidebar.beta_expander(label="Show Paths:", expanded=False):
    st.markdown(f"### Model Store Path: \n {model_store}")
    st.markdown(f"### Config Path: \n {config_path}")
    st.markdown(f"### Log Location: \n {log_location}")
    st.markdown(f"### Metrics Location: \n {metrics_location}")

start = st.sidebar.button("Start Torchserve")
if start:
    last_res()[0]= tsa.start_torchserve(model_store, config_path, log_location, metrics_location)
    rerun()

stop = st.sidebar.button("Stop Torchserve")
if stop:
    last_res()[0] = tsa.stop_torchserve()
    rerun()

loaded_models = tsa.get_loaded_models(M_API)
if loaded_models:
    loaded_models_names = [m["modelName"] for m in loaded_models["models"]]
else:
    st.header("Torchserve is down...")
st.sidebar.subheader("Loaded models")
st.sidebar.write(loaded_models)

stored_models = get_model_store()
st.sidebar.subheader("Available models")
st.sidebar.write(stored_models)
####################

st.header("Last Message:")
st.write(last_res()[0])

with st.beta_expander(label="Show torchserve config", expanded=False):
    st.write(config)
    st.markdown("[configuration docs](https://pytorch.org/serve/configuration.html)")

if loaded_models:

    with st.beta_expander(label="Register a model", expanded=False):

        st.markdown("# Register a model [(docs)](https://pytorch.org/serve/management_api.html#register-a-model)")
        placeholder = st.empty()
        mar_path = placeholder.selectbox("Choose mar file *", [default_key] + stored_models, index=0)
        # mar_path = os.path.join(model_store,mar_path)
        p = st.checkbox("or use another path")
        if p:
            mar_path = placeholder.text_input("Input mar file path*")
        model_name = st.text_input(label="Model name (overrides predefined)")
        col1, col2 = st.beta_columns(2)
        batch_size = col1.number_input(label="batch_size", value=0, min_value=0, step=1)
        max_batch_delay = col2.number_input(label="max_batch_delay", value=0, min_value=0, step=100)
        initial_workers = col1.number_input(label="initial_workers", value=1, min_value=0, step=1)
        response_timeout = col2.number_input(label="response_timeout", value=0, min_value=0, step=100)
        handler = col1.text_input(label="handler")
        runtime = col2.text_input(label="runtime")

        proceed = st.button("Register")
        if proceed:
            if mar_path != default_key:
                st.write(f"Registering Model...{mar_path}")
                res = tsa.register_model(
                    M_API,
                    mar_path,
                    model_name,
                    handler=handler,
                    runtime=runtime,
                    batch_size=batch_size,
                    max_batch_delay=max_batch_delay,
                    initial_workers=initial_workers,
                    response_timeout=response_timeout,
                )
                last_res()[0] = res
                rerun()
            else:
                st.write(":octagonal_sign: Fill the required fileds!")
        
            

    with st.beta_expander(label="Remove a model", expanded=False):

        st.header("Remove a model")
        model_name = st.selectbox("Choose model to remove", [default_key] + loaded_models_names, index=0)
        if model_name != default_key:
            default_version = tsa.get_model(M_API, model_name)[0]["modelVersion"]
            st.write(f"default version {default_version}")
            versions = tsa.get_model(M_API, model_name, list_all=True)
            versions = [m["modelVersion"] for m in versions]
            version = st.selectbox("Choose version to remove", [default_key] + versions, index=0)
            proceed = st.button("Remove")
            if proceed:
                if model_name != default_key and version != default_key:
                    res = tsa.delete_model(M_API, model_name, version)
                    last_res()[0] = res
                    rerun()
                else:
                    st.write(":octagonal_sign: Pick a model & version!")
                    
    with st.beta_expander(label="Get model details", expanded=False):

        st.header("Get model details")
        model_name = st.selectbox("Choose model", [default_key] + loaded_models_names, index=0)
        if model_name != default_key:
            default_version = tsa.get_model(M_API,model_name)[0]["modelVersion"]
            st.write(f"default version {default_version}")
            versions = tsa.get_model(M_API,model_name, list_all=False)
            versions = [m["modelVersion"] for m in versions]
            version = st.selectbox("Choose version", [default_key, "All"] + versions, index=0)
            if model_name != default_key:
                if version == "All":
                    res = tsa.get_model(M_API, model_name, list_all=True)
                    st.write(res)
                elif version != default_key:
                    res = tsa.get_model(M_API, model_name, version)
                    st.write(res)
                    
    with st.beta_expander(label="Scale workers", expanded=False):
        st.markdown("# Scale workers [(docs)](https://pytorch.org/serve/management_api.html#scale-workers)")
        model_name = st.selectbox("Pick model", [default_key] + loaded_models_names, index=0)
        if model_name != default_key:
            default_version = tsa.get_model(M_API,model_name)[0]["modelVersion"]
            st.write(f"default version {default_version}")
            versions = tsa.get_model(M_API,model_name, list_all=False)
            versions = [m["modelVersion"] for m in versions]
            version = st.selectbox("Choose version", ["All"] + versions, index=0)
            
            col1, col2, col3 = st.beta_columns(3)
            min_worker = col1.number_input(label="min_worker(optional)", value=-1, min_value=-1, step=1)
            max_worker = col2.number_input(label="max_worker(optional)", value=-1, min_value=-1, step=1)
            number_gpu = col3.number_input(label="number_gpu(optional)", value=-1, min_value=-1, step=1)
            proceed = st.button("Apply")
            if proceed and model_name != default_key:
                # number_input can't be set to None
                if version == "All":
                    version=None
                if min_worker == -1:
                    min_worker=None
                if max_worker == -1:
                    max_worker=None
                if number_gpu == -1:
                    number_gpu=None
                
                res = tsa.change_model_workers(M_API, model_name, version=version, min_worker=min_worker, max_worker=max_worker, number_gpu=number_gpu)
                last_res()[0] = res
                rerun()

