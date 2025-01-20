import uvicorn, os
from dotenv import load_dotenv
from summarization import SummarizationApplication

if __name__ == "__main__":
    load_dotenv(verbose=True, override=True)
    app = SummarizationApplication.generate()
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
