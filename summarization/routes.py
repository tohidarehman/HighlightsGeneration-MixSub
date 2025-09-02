from fastapi import APIRouter, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi_utils.cbv import cbv
import os
import re
import sys
import requests
from .models import (
    SummarizationRequest,
    SummarizationResponse,
    AvailableModel,
    ModelTask,
)


apis_router = APIRouter(prefix="/api")
view_router = APIRouter()  # This is mounted with the root route i.e. '/'


@cbv(apis_router)
class ApisCBV:
    def __init__(self):
        self.__timeout_in_seconds = 180
        self.__authorization_token = os.getenv("HF_TOKEN")

    def remove_comma_after_full_stop(self, text: str):
        return re.sub(r"\.\;", ".", text)

    def query(self, model_name: str, payload):
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {
            "Authorization": f"Bearer {self.__authorization_token}",
        }
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.__timeout_in_seconds,
            )
            return response.json()
        except Exception as err: 
            print("Error Occurred: ", err.__repr__(), file=sys.stderr)
            raise err

    @apis_router.post("/generate")
    def summarize(self, body: SummarizationRequest) -> SummarizationResponse:
        if self.__authorization_token is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="HuggingFace Inference Endpoint Token Missing",
            )

        input_text = body.paper_content
        model_name = body.preferred_model
        maximum_tokens = body.maximum_tokens

        prefix = "summarize: "
        text_with_prefix = prefix + input_text

        if body.inference_task == ModelTask.TEXT_GENERATION:
            parameters = {
                "max_new_tokens": maximum_tokens,
                "do_sample": False,
                # "return_full_text": False,
            }
        else:
            parameters = {}

        try:
            resp = self.query(
                model_name,
                {
                    "inputs": text_with_prefix,
                    "parameters": parameters,
                },
            )

            if "error" in resp:
                raise Exception(resp)

            if body.inference_task == ModelTask.SUMMARIZATION:
                out_text = resp[0]["summary_text"]
            elif body.inference_task == ModelTask.TEXT_GENERATION:
                out_text = resp[0]["generated_text"]
            else:
                out_text = "`summary_text` or `generated_text` not present."

        except Exception as err:
            print("Error Occurred: ", err.__repr__(), file=sys.stderr)
            out_text = err.__repr__()

        generated_text = self.remove_comma_after_full_stop(out_text)
        return SummarizationResponse(output=generated_text)


@cbv(view_router)
class ViewCBV:
    templates = Jinja2Templates("templates")

    available_models = (
        #AvailableModel(
            #hf_model_id="TRnlp/LLAMA-3-8B-TS-MixSub",
            #display_name="LLAMA-3-8B-TS-MixSub",
            #task=ModelTask.TEXT_GENERATION,
        #),
        AvailableModel(
            hf_model_id="TRnlp/BART-base-MixSub-TS",
            display_name="BART-base-MixSub-TS",
            task=ModelTask.TEXT_GENERATION,
        ),
        AvailableModel(
            hf_model_id="TRnlp/T5-base-MixSub-TS",            
            display_name="T5-base-MixSub-TS",
            task=ModelTask.TEXT_GENERATION,
        ),
    )

    @view_router.get("/", response_class=HTMLResponse)
    def home(self, request: Request):
        return self.templates.TemplateResponse(
            request,
            "application.html",
            {
                "PageHeading": "Research Highlight Generation",
                "Models": self.available_models,
            },
        )
