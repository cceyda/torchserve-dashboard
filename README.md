# Torchserve Dashboard

Torchserve Dashboard using Streamlit

Related blog [post](https://cceyda.github.io/blog/torchserve/streamlit/dashboard/2020/10/15/torchserve.html)

![Demo](assets/dashboard_demo.gif)

# Usage
Additional Requirement: 
[torchserve](https://github.com/pytorch/serve/tree/v0.3.1#install-torchserve-and-torch-model-archiver) (recommended:v0.3.1)

Simply run:

```bash
pip3 install torchserve-dashboard --user
# torchserve-dashboard [streamlit_options(optional)] -- [config_path(optional)] [model_store(optional)] [log_location(optional)] [metrics_location(optional)]
torchserve-dashboard
#OR change port 
torchserve-dashboard --server.port 8105 -- --config_path ./torchserve.properties
#OR provide a custom configuration 
torchserve-dashboard -- --config_path ./torchserve.properties --model_store ./model_store
```

:exclamation: Keep in mind that If you change any of the `--config_path`,`--model_store`,`--metrics_location`,`--log_location` options while there is a torchserver already running before starting torch-dashboard they won't come into effect until you stop&start torchserve.

OR 
```bash
git clone https://github.com/cceyda/torchserve-dashboard.git
streamlit run torchserve_dashboard/dash.py 
#OR
streamlit run torchserve_dashboard/dash.py --server.port 8105 -- --config_path ./torchserve.properties 
```
Example torchserve [config](https://pytorch.org/serve/configuration.html):

```
inference_address=http://127.0.0.1:8443
management_address=http://127.0.0.1:8444
metrics_address=http://127.0.0.1:8445
grpc_inference_port=7070
grpc_management_port=7071
number_of_gpu=0
batch_size=1
model_store=./model_store
```

If the server doesn't start for some reason check if your ports are already in use!

# Updates

[15-oct-2020] add [scale workers](https://pytorch.org/serve/management_api.html#scale-workers) tab 

[16-feb-2021] (functionality) make logpath configurable,(functionality)remove model_name requirement,(UI)add cosmetic error messages

[10-may-2021] update config & make it optional. update streamlit. Auto create folders

# FAQs
- **Does torchserver keep running in the background?**

    The torchserver is spawned using `Popen` and keeps running in the background even if you stop the dashboard.

- **What about environment variables?**

    These environment variables are passed to the torchserve command:
    
    `ENVIRON_WHITELIST=["LD_LIBRARY_PATH","LC_CTYPE","LC_ALL","PATH","JAVA_HOME","PYTHONPATH","TS_CONFIG_FILE","LOG_LOCATION","METRICS_LOCATION"]`

- **How to change the logging format of torchserve?**

    You can set the location of your custom log4j config in your configuration file as in [here](https://pytorch.org/serve/logging.html#provide-with-config-properties)
    
    `vmargs=-Dlog4j.configuration=file:///path/to/custom/log4j.properties`
    
- **What is the meaning behind the weird versioning**?

    The minor follows the compatible torchserve version, patch version reflects the dashboard versioning
    
# Help & Question & Feedback

Open an issue


