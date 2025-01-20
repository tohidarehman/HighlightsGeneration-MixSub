from fastapi import APIRouter, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi_utils.cbv import cbv
import huggingface_hub
import os
import re
import sys
from .models import (
    SummarizationRequest,
    SummarizationResponse,
    AvailableModel,
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

        try:
            llm_client = huggingface_hub.InferenceClient(
                model=model_name,
                timeout=self.__timeout_in_seconds,
                token=self.__authorization_token,
            )
            op = llm_client.text_generation(
                model=model_name,
                prompt=text_with_prefix,
                max_new_tokens=maximum_tokens,
                do_sample=False,
                return_full_text=False,
                details=True,
            )
            generated_text = self.remove_comma_after_full_stop(
                op.generated_text
            )
        except Exception as err:
            print(err.__repr__(), file=sys.stderr)
            generated_text = err.__repr__()

        return SummarizationResponse(output=generated_text)


@cbv(view_router)
class ViewCBV:
    templates = Jinja2Templates("templates")

    available_models = (
        AvailableModel(
            hf_model_id="TRnlp/BART-base-MixSub-TS",
            display_name="BART-base-MixSub-TS",
        ),
        AvailableModel(
            hf_model_id="TRnlp/T5-base-MixSub-TS",
            display_name="T5-base-MixSub-TS",
        ),
        AvailableModel(
            hf_model_id="facebook/bart-large-cnn",
            display_name="facebook/bart-large-cnn",
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
