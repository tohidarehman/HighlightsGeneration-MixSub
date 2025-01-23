import fastapi, fastapi.responses
import huggingface_hub, pydantic, os


api_router = fastapi.APIRouter(prefix="/api")


@api_router.get("/available-models")
def available_models():
    available_models_list = [
        {
            "modelId": "TRnlp/BART-base-MixSub-TS",
            "displayName": "BART-base-MixSub-TS",
        },
        {
            "modelId": "TRnlp/t5-check",
            "displayName": "T5-base-MixSub-TS",
        },
        #{
            #"modelId": "TRnlp/LLAMA-3-8B-TS-MixSub",
            #"displayName": "LLAMA-3-8B-TS-MixSub",
        #},
    ]

    return {"models": available_models_list}


class SummarizationRequest(pydantic.BaseModel):
    elaborate_text: str
    summarization_model: str
    maximum_tokens: int
    use_huggingface_model: bool


@api_router.post("/summarize")
def summarize(request: SummarizationRequest):
    input_text = request.elaborate_text
    model_name = request.summarization_model
    maximum_tokens = request.maximum_tokens

    prefix = "summarize: "
    text_with_prefix = prefix + input_text

    timeout_in_seconds = 180
    authorization_token = os.getenv("HF_TOKEN")
    if authorization_token is None:
        return {"output": "no authorization token provided. contact administrator."}

    llm_client = huggingface_hub.InferenceClient(
        model=model_name,
        timeout=timeout_in_seconds,
        token=authorization_token,
    )

    try:
        generated_text = llm_client.text_generation(
            model=model_name,
            prompt=text_with_prefix,
            max_new_tokens=maximum_tokens,
            do_sample=False,
            return_full_text=False,
        )
    except Exception as err:
        generated_text = err.__repr__()

    # tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
    # model: transformers.PreTrainedModel = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_name)
    # inputs = tokenizer(
    #     text_with_prefix,
    #     return_tensors="pt",
    #     max_length=512,
    #     truncation=True,
    #     padding=True,
    # )
    # predictions = model.generate(
    #     input_ids=inputs["input_ids"],
    #     attention_mask=inputs["attention_mask"],
    #     max_length=maximum_tokens,
    #     num_beams=4,
    #     do_sample=False,
    #     min_length=3,
    # )
    # generated_text = tokenizer.decode(predictions[0], skip_special_tokens=True)

    return {"output": generated_text}
