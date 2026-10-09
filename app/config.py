import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    VECTOR_DB_PATH = "vector_db"

    # =====================================================================
    # DEFINE THE ROUTING POOL (DEPLOYMENT ARCHITECTURE)
    # =====================================================================
    MODEL_LIST = [
                {
                    "model_name": "resilient-llm-pool",
                    "litellm_params": {
                        "model": "openai/gpt-4o-mini",
                        "api_key": OPENAI_API_KEY,
                        "rpm": 500,
                    },
                },
                {
                    "model_name": "resilient-llm-pool",
                    "litellm_params": {
                        "model": "openai/gpt-4o",
                        "api_key": OPENAI_API_KEY,
                        "rpm": 500,
                    },
                }
            ]