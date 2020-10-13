# Torchserve Dashboard

Torchserve Dashboard using streamlit

Related blog [post](https://cceyda.github.io/blog/torchserve/streamlit/dashboard/2020/10/15/torchserve.html)

![Demo](assets/dashboard_demo.gif)

# Usage

Simply run:

```bash
pip3 install torchserve-dashboard
# torchserve-dashboard [streamlit_options] -- [config_path] [model_store(optional)]
torchserve-dashboard --server.port 8105 -- --config_path ./torchserve.properties --model_store ./model_store
```
OR 
```bash
git clone https://github.com/cceyda/torchserve-dashboard.git
streamlit run torchserve_dashboard/dash.py --server.port 8105 -- --config_path ./torchserve.properties 
```
Example torchserve [config](https://pytorch.org/serve/configuration.html):

```
inference_address=http://127.0.0.1:8443
management_address=http://127.0.0.1:8444
metrics_address=http://127.0.0.1:8445
number_of_gpu=0
batch_size=1
model_store=/mnt/pretrained/model_store
```
# Help

Open an issue


