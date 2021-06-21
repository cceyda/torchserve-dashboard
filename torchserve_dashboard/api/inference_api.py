import os
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

import httpx
from httpx import Response

import logging

class InferenceAPI:
    def __init__(self, address: str, error_callback: Callable = None) -> None:
        pass

    # get available models
    # determine type of model (NOT currently possible, we don't know which endpoint maps to what type)
    # auto generate python client based on model spec? (use library)
    # or define explicitly like below (not sustainable)
    def image_classify(endpoint,image):
        # put image in request body
        # 
        # res send(address+endpoint,req)
        # return res
        pass
