from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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

# Routers
apis_router = APIRouter(prefix="/api")
view_router = APIRouter()  # Root route '/'

# Load models locally at startup
print("Loading Hugging Face models locally...", file=sys.stderr)
summarizer_bart = pipeline("summarization", model="facebook/bart-large-cnn")
print("Models loaded successfully ✅", file=sys.stderr)


@cbv(apis_router)
class ApisCBV:
    def remove_comma_after_full_stop(self, text: str):
        return re.sub(r"\.\;", ".", text)

    def query_local(self, model_name: str, text: str, maximum_tokens: int):
        """Run summarization locally."""
        if "BART" in model_name:
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
            out_text = resp[0]["summary_text"]

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
            hf_model_id="facebook/bart-large-cnn",
            display_name="BART-large-CNN",
            task=ModelTask.SUMMARIZATION,
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
