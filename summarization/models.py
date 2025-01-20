from fastapi_utils.api_model import APIModel


class SummarizationRequest(APIModel):
    paper_content: str
    preferred_model: str
    maximum_tokens: int


class SummarizationResponse(APIModel):
    output: str


class AvailableModel:
    def __init__(self, hf_model_id: str, display_name: str):
        self.hf_model_id = hf_model_id
        self.display_name = display_name

    def __hash__(self):
        return hash((self.hf_model_id, self.display_name))
