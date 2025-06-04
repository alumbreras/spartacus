from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)
client = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_MODEL"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )


if __name__ == "__main__":
    print(client.invoke("Hello, world!"))