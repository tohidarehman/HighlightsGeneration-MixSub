from fastapi import APIRouter, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi_utils.cbv import cbv
import re
import sys

from transformers import pipeline

from .models import (
    SummarizationRequest,
    SummarizationResponse,
    AvailableModel,
    ModelTask,
)

# Define routers
apis_router = APIRouter(prefix="/api")
view_router = APIRouter()  # This is mounted with the root route i.e. '/'

# Load models once at startup (local pipeline, not remote API)
print("Loading Hugging Face models locally...", file=sys.stderr)
summarizer_t5 = pipeline("summarization", model="TRnlp/T5-base-MixSub-TS")
summarizer_bart = pipeline("summarization", model="TRnlp/BART-base-MixSub-TS")
print("Models loaded successfully ✅", file=sys.stderr)


@cbv(apis_router)
class ApisCBV:
    def __init__(self):
        self.__timeout_in_seconds = 180  # kept for consistency, not used now

    def remove_comma_after_full_stop(self, text: str):
        return re.sub(r"\.\;", ".", text)

    def query_local(self, model_name: str, text: str, maximum_tokens: int):
        """Run summarization locally using transformers pipeline."""
        if "T5-base-MixSub-TS" in model_name:
            return summarizer_t5(text, max_length=maximum_tokens)
        elif "BART-base-MixSub-TS" in model_name:
            return summarizer_bart(text, max_length=maximum_tokens)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    @apis_router.post("/generate")
    def summarize(self, body: SummarizationRequest) -> SummarizationResponse:
        input_text = body.paper_content
        model_name = body.preferred_model
        maximum_tokens = body.maximum_tokens

        prefix = "summarize: "
        text_with_prefix = prefix + input_text

        try:
            resp = self.query_local(model_name, text_with_prefix, maximum_tokens)

            if body.inference_task == ModelTask.SUMMARIZATION:
                out_text = resp[0]["summary_text"]
            elif body.inference_task == ModelTask.TEXT_GENERATION:
                out_text = resp[0]["summary_text"]  # both use summarizer
            else:
                out_text = "`summary_text` not present."

        except Exception as err:
            print("Error Occurred: ", err.__repr__(), file=sys.stderr)
            out_text = err.__repr__()

        generated_text = self.remove_comma_after_full_stop(out_text)
        return SummarizationResponse(output=generated_text)


@cbv(view_router)
class ViewCBV:
    templates = Jinja2Templates("templates")

    available_models = (
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
