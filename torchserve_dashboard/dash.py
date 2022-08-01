import argparse
import os

import streamlit as st
from httpx import Response

from torchserve_dashboard.api import ManagementAPI, LocalTS
from pathlib import Path 

st.set_page_config(
    page_title="Torchserve Management Dashboard",
    page_icon="./icon.png",
    layout="centered",
    initial_sidebar_state="expanded",
)

def rerun():
    st.experimental_rerun()

def error_callback(response:Response):
    if response.status_code != 200:
        st.write("There was an error!")
        st.write(response)

@st.cache(allow_output_mutation=True)
def last_res():
    return ["Nothing"]

@st.experimental_singleton(suppress_st_warning=True)
def check_args(_args):

    args=_args
    M_API = "http://127.0.0.1:8081"
    model_store = args.model_store
    config_path = args.config_path
    log_location = args.log_location
    metrics_location = args.metrics_location
    log_config = args.log_config
    if not os.path.exists(config_path):
        st.write(f"Can't find config file at {config_path}. Using default config instead")
        config_path = os.path.join(os.path.dirname(__file__), "default.torchserve.properties")
    if os.path.exists(config_path):
        config = open(config_path, "r").readlines()
        for c in config:
            if c.startswith("model_store"):
                if not model_store:
                    model_store = c.split("=")[-1].strip()
            if c.startswith("management_address"):
                M_API = c.split("=")[-1].strip()
    else:
        st.write("Config file can't be found!")

    if log_location:
        log_location = str(Path(log_location).resolve())
    if metrics_location:
        metrics_location = str(Path(metrics_location).resolve())
    if model_store:
        model_store = str(Path(model_store).resolve())

    if model_store is None:
        st.write("model_store is required!")
        st.stop()

    if not os.path.isdir(model_store):
        st.write(f"Created model store directory {model_store}")
        os.makedirs(model_store, exist_ok=True)

    return M_API, config, model_store, config_path, log_location, metrics_location, log_config

@st.experimental_singleton(suppress_st_warning=True)
def initialize(_args):
    # Initialization should be done once! 
    # As a design choice config_path,log_location,metrics_location are non-editable from the UI as a semi-security measure. Can only pass from command line.
    api_address, config, model_store, config_path, log_location, metrics_location, log_config = check_args(_args)
    api = ManagementAPI(api_address, error_callback)
    ts = LocalTS(model_store, config_path, log_location, metrics_location, log_config)
    torchserve_status = api.get_loaded_models()
    if not torchserve_status and args.init:
        st.write("Starting Torchserve")
        last_res()[0] = ts.start_torchserve()
        rerun()
    return config, api, ts

def dashboard(args):
    st.title("Torchserve Management Dashboard")
    default_key = "None"
    config, api, ts = initialize(args)
    ts_version,ts_error=ts.check_version() # doing it this way rather than ts.__version__ on purpose
    if ts_error:
        st.error(ts_error)
        st.stop()

    support_workflow=False #Temp workaround
    if '0.4' in ts_version:
        support_workflow=True

    ##########Sidebar##########
    st.sidebar.markdown("## Help")
    with st.sidebar.expander(label="Show Paths:", expanded=False):
        st.markdown(f"### Model Store Path: \n {ts.model_store}")
        st.markdown(f"### Config Path: \n {ts.config_path}")
        st.markdown(f"### Log Location: \n {ts.log_location}")
        st.markdown(f"### Metrics Location: \n {ts.metrics_location}")
    st.sidebar.write(ts_version)
    start = st.sidebar.button("Start Torchserve")
    if start:
        last_res()[0] = ts.start_torchserve()
        rerun()

    stop = st.sidebar.button("Stop Torchserve")
    if stop:
        last_res()[0] = ts.stop_torchserve()
        rerun()

    torchserve_status = api.get_loaded_models()
    if torchserve_status:
        loaded_models_names = [m["modelName"] for m in torchserve_status["models"]]
    else:
        st.header("Torchserve is down...")
    st.sidebar.subheader("Loaded models")
    st.sidebar.write(torchserve_status)

    stored_models = ts.get_model_store()
    st.sidebar.subheader("Available models")
    st.sidebar.write(stored_models)
    ####################

    st.markdown(f"**Last Message**: {last_res()[0]}")

    with st.expander(label="Show torchserve config", expanded=False):
        st.write(config)
        st.markdown("[configuration docs](https://pytorch.org/serve/configuration.html)")

    if torchserve_status:

        with st.expander(label="Register a model", expanded=False):

            st.markdown(
                "# Register a model [(docs)](https://pytorch.org/serve/management_api.html#register-a-model)"
            )
            placeholder = st.empty()
            mar_path = placeholder.selectbox(
                "Choose mar file *", [default_key] + stored_models, index=0
            )
            p = st.checkbox("manually enter location")
            if p:
                mar_path = placeholder.text_input("Input mar file path*")
            
            model_name = st.text_input(label="Model name (overrides predefined)")
            col1, col2 = st.columns(2)
            batch_size = col1.number_input(label="batch_size", value=0, min_value=0, step=1)
            max_batch_delay = col2.number_input(
                label="max_batch_delay", value=0, min_value=0, step=100
            )
            initial_workers = col1.number_input(
                label="initial_workers", value=1, min_value=0, step=1
            )
            response_timeout = col2.number_input(
                label="response_timeout", value=0, min_value=0, step=100
            )
            handler = col1.text_input(label="handler")
            runtime = col2.text_input(label="runtime")
            is_encrypted = st.checkbox("SSE-KMS Encrypted", help="Refer to https://github.com/pytorch/serve/blob/v0.5.0/docs/management_api.md#encrypted-model-serving")
            proceed = st.button("Register")
            if proceed:
                if mar_path != default_key:
                    st.write(f"Registering Model...{mar_path}")
                    res = api.register_model(
                        mar_path,
                        model_name,
                        handler=handler,
                        runtime=runtime,
                        batch_size=batch_size,
                        max_batch_delay=max_batch_delay,
                        initial_workers=initial_workers,
                        response_timeout=response_timeout,
                        is_encrypted=is_encrypted,
                    )
                    last_res()[0] = res
                    rerun()
                else:
                    st.warning(":octagonal_sign: Fill the required fileds!")

        with st.expander(label="Remove a model", expanded=False):

            st.header("Remove a model")
            model_name = st.selectbox(
                "Choose model to remove", [default_key] + loaded_models_names, index=0
            )
            if model_name != default_key:
                default_version = api.get_model(model_name)[0]["modelVersion"]
                st.write(f"default version {default_version}")
                versions = api.get_model(model_name, list_all=True)
                versions = [m["modelVersion"] for m in versions]
                version = st.selectbox(
                    "Choose version to remove", [default_key] + versions, index=0
                )
                proceed = st.button("Remove")
                if proceed:
                    if model_name != default_key and version != default_key:
                        res = api.delete_model(model_name, version)
                        last_res()[0] = res
                        rerun()
                    else:
                        st.warning(":octagonal_sign: Pick a model & version!")

        with st.expander(label="Get model details", expanded=False):

            st.header("Get model details")
            model_name = st.selectbox(
                "Choose model", [default_key] + loaded_models_names, index=0
            )
            if model_name != default_key:
                default_version = api.get_model(model_name)[0]["modelVersion"]
                st.write(f"default version {default_version}")
                versions = api.get_model(model_name, list_all=False)
                versions = [m["modelVersion"] for m in versions]
                version = st.selectbox(
                    "Choose version", [default_key, "All"] + versions, index=0
                )
                custom_metadata = st.checkbox("Return custom metadata (may freeze/error if not exists!)")
                if model_name != default_key:
                    if version == "All":
                        res = api.get_model(model_name, list_all=True, custom_metadata=custom_metadata)
                        st.write(res)
                    elif version != default_key:
                        res = api.get_model(model_name, version, custom_metadata=custom_metadata)
                        st.write(res)

        with st.expander(label="Scale workers", expanded=False):
            st.markdown(
                "# Scale workers [(docs)](https://pytorch.org/serve/management_api.html#scale-workers)"
            )
            model_name = st.selectbox(
                "Pick model", [default_key] + loaded_models_names, index=0
            )
            if model_name != default_key:
                default_version = api.get_model(model_name)[0]["modelVersion"]
                st.write(f"default version {default_version}")
                versions = api.get_model(model_name, list_all=False)
                versions = [m["modelVersion"] for m in versions]
                version = st.selectbox("Choose version", ["All"] + versions, index=0)

                col1, col2, col3 = st.columns(3)
                min_worker = col1.number_input(
                    label="min_worker(optional)", value=-1, min_value=-1, step=1
                )
                max_worker = col2.number_input(
                    label="max_worker(optional)", value=-1, min_value=-1, step=1
                )
                #             number_gpu = col3.number_input(label="number_gpu(optional)", value=-1, min_value=-1, step=1)
                proceed = st.button("Apply")
                if proceed and model_name != default_key:
                    # number_input can't be set to None
                    if version == "All":
                        version = None
                    if min_worker == -1:
                        min_worker = None
                    if max_worker == -1:
                        max_worker = None
                    #                 if number_gpu == -1:
                    #                     number_gpu=None

                    res = api.change_model_workers(model_name,
                                                version=version,
                                                min_worker=min_worker,
                                                max_worker=max_worker,
                                                #                     number_gpu=number_gpu,
                                                )
                    last_res()[0] = res
                    rerun()
        if support_workflow:
            with st.expander(label="Register Workflow", expanded=False):
                st.markdown(
                    "# Register a workflow [(docs)](https://pytorch.org/serve/workflow_management_api.html#register-a-workflow)"
                )
                url = st.text_input("Input war file path or URI *")
                workflow_name = st.text_input(label="Workflow name (overrides predefined)")
                if url:
                    res = api.register_workflow(url, workflow_name)
                    st.write(res)

            with st.expander(label="Show Workflow Details", expanded=False):
                st.markdown(
                    "# Describe a workflow [(docs)](https://pytorch.org/serve/workflow_management_api.html#describe-workflow)"
                )
                loaded_workflows = api.list_workflows()  # only upto 100 TODO
                if loaded_workflows and ("workflows" in loaded_workflows):
                    loaded_workflow_names = [w["workflowName"] for w in loaded_workflows["workflows"]]
                    workflow_name = st.selectbox(
                        "Pick workflow", [default_key] + loaded_workflow_names, index=0
                    )
                    if workflow_name != default_key:
                        res = api.get_workflow(workflow_name)
                        st.write(res)

            with st.expander(label="Unregister Workflow", expanded=False):
                st.markdown(
                    "# Unregister a Workflow [(docs)](https://pytorch.org/serve/workflow_management_api.html#unregister-a-workflow)"
                )
                loaded_workflows = api.list_workflows()  # only upto 100
                if loaded_workflows and ("workflows" in loaded_workflows):
                    loaded_workflow_names = [w["workflowName"] for w in loaded_workflows["workflows"]]
                    workflow_name = st.selectbox(
                        "Unregister workflow", [default_key] + loaded_workflow_names, index=0
                    )
                    if workflow_name != default_key:
                        res = api.unregister_workflow(workflow_name)
                        st.write(res)

            with st.expander(label="List Workflows", expanded=False):
                st.markdown(
                    "# List Workflows"
                )
                workflows = []
                loaded_workflows = api.list_workflows()
                if loaded_workflows:
                    if "workflows" in loaded_workflows:
                        workflows.extend(loaded_workflows["workflows"])
                st.write(workflows)

if __name__ == "__main__":
    # Should probably handle argparse in cli.py with click 
    # but not sure how that would effect passing params to streamlit
    parser = argparse.ArgumentParser(description="Torchserve Dashboard")

    parser.add_argument(
        "--model_store", 
        default=None, 
        help="Directory where your models are stored (overrides config)"
    )
    parser.add_argument(
        "--config_path",
        default="./torchserve.properties",
        help="Torchserve config path",
    )
    parser.add_argument(
        "--log_location",
        default="./logs/",
        help="Passed as environment variable LOG_LOCATION to Torchserve",
    )
    parser.add_argument(
        "--metrics_location",
        default="./logs/metrics/",
        help="Passed as environment variable METRICS_LOCATION to Torchserve",
    )
    parser.add_argument(
        "--log_config",
        default=None,
        help="Overrides the default log4j.properties",
    )
    parser.add_argument(
        "--init",
        action='store_true',
        help="Starts torchserve",
    )
    try:
        args = parser.parse_args()
    except SystemExit as e:
        os._exit(e.code)

    dashboard(args)