import os
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

import httpx
from httpx import Response

import logging

log = logging.getLogger(__name__)


class InferenceAPI:
    def __init__(self,
                 address: str,
                 error_callback: Optional[Callable] = None) -> None:
        self.address = address
        if not error_callback:
            error_callback = self.default_error_callback
        self.client = httpx.Client(timeout=1000,
                                   event_hooks={"response": [error_callback]})

    @staticmethod
    def default_error_callback(response: Response) -> None:
        if response.status_code != 200:
            log.info(f"Warn - status code: {response.status_code},{response}")

    # get available models
    # determine type of model (NOT currently possible, we don't know which endpoint maps to what type)
    # auto generate python client based on model spec? (use library)
    # or define explicitly like below (not sustainable)
    def image_classify(endpoint, image):
        # put image in request body
        #
        # res send(address+endpoint,req)
        # return res
        pass

    ### Model
    def get_predictions(self,
                        input_,
                        model_name: str,
                        version: Optional[str] = None):
        """Get the prediction of a model according to the provided input.

        CURL equivalence:
            curl http://localhost:8080/predictions/resnet-18/2.0 -T kitten_small.jpg
                or
            curl http://localhost:8080/predictions/resnet-18/2.0 -F "data=@kitten_small.jpg"

        Args:
            input_ ([type]): Buffer or Tensor to send to the endpoint as payload
            model_name (str): name of the model to use
            version (Optional[str]): Version number of the model. Defaults to None.

        Returns:
            httpx.Response: The response from the Torch server.
        """
        req_url = self.address + '/predictions/' + model_name
        if version:
            req_url += '/' + version
        res: Response = self.client.post(req_url, files={'data': input_})
        return res

    def get_explanations(self,
                         input_,
                         model_name: str,
                         version: Optional[str] = None):
        """Get Explanations from the model.
        (sets is_explain to True in the model handler, which leads to calling its the ``explain_handle`` method).

        CURL equivalence:
            curl http://localhost:8080/explanations/resnet-18/2.0 -T kitten_small.jpg
                or
            curl http://localhost:8080/explanations/resnet-18/2.0 -F "data=@kitten_small.jpg"

        Args:
            input_ ([type]): Buffer or Tensor to send to the endpoint as payload
            model_name (str): name of the model to use
            version (Optional[str]): Version number of the model. Defaults to None.

        Returns:
            httpx.Response: The response from the Torch server.
        """
        req_url = self.address + '/explanations/' + model_name
        if version:
            req_url += '/' + version
        res: Response = self.client.post(req_url, files={'data': input_})
        return res

    ### Workflow
    def get_workflow_predictions(self, input_: str, workflow_name: str):
        """Get the prediction of a model according to the provided input.

        CURL equivalence:
            curl http://localhost:8080/wfpredict/myworkflow -T kitten_small.jpg
                or
            curl http://localhost:8080/wfpredict/myworkflow -F "data=@kitten_small.jpg"

        Args:
            input_ ([type]): Buffer or Tensor to send to the endpoint as payload
            model_name (str): name of the model to use

        Returns:
            httpx.Response: The response from the Torch server.
        """
        req_url = self.address + '/wfpredict/' + workflow_name
        res: Response = self.client.post(req_url, files={'data': input_})
        return res