from pydantic import SecretStr
from pydantic_settings import BaseSettings


class OpenAIConfig(BaseSettings):
    OPENAI_TOKEN: SecretStr
    MODEL_VERSION: str = 'gpt-4-turbo'


settings = OpenAIConfig()
