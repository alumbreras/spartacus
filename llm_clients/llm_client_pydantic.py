from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os

load_dotenv(override=True)
client = AsyncAzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )


azure_openai_model = OpenAIModel(
    model_name=os.getenv("AZURE_OPENAI_MODEL"),
    provider=OpenAIProvider(openai_client=client),
)