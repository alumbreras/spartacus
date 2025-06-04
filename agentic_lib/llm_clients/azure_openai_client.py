import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, TypeVar
from openai import AsyncAzureOpenAI as AzureOpenAI
from pydantic import BaseModel

# Load environment variables from the root .env file
load_dotenv(override=True, dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# API version "2024-06-01" # tool_choice='required' available from this version
# API version "2024-08-01-preview" # structured output available from this version

# tried APIs:
# "2024-08-06": resource not available
# 2024-07-01-preview:  code: 400 - {'error': {'code': 'BadRequest', 'message': 'response_format value as json_schema is enabled only for api versions 2024-08-01-preview and later'}}
# 2024-08-01-preview: BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs", 'type': 'invalid_request_error', 'param': None, 'code': None}}
# 2024-09-01-preview: BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs", 'type': 'invalid_request_error', 'param': None, 'code': None}}
# 2024-10-01-preview: BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs", 'type': 'invalid_request_error', 'param': None, 'code': None}}
# 2024-11-01-preview: BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model. Learn more about supported models at the Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs", 'type': 'invalid_request_error', 'param': None, 'code': None}}


# Some useful properties of the OpenAI response:
# completion.choices[0].message.content
# completion.choices[0].message.tool_calls
# completion.choices[0].message.tool_calls[0].function.arguments
# completion.choices[0].message.tool_calls[0].function.name


MAX_TOKENS = 16384

T = TypeVar('T', bound=BaseModel)

class AzureOpenAIClient():
    """
    Client for interacting with Azure OpenAI API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None
    ):
        load_dotenv(override=True)
        self.client = AzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=api_version or os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_MODEL")
    
    async def invoke(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> Any:
        response = await self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        return response.choices[0].message
    
    async def invoke_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:

        response = await self.client.beta.chat.completions.parse(
            model=self.deployment_name,
            messages=messages,
            response_format=response_format,
            **kwargs
        )
        
        return response.choices[0].message.parsed