from pydantic import SecretStr
from pydantic_settings import BaseSettings


class OpenAIConfig(BaseSettings):
    OPENAI_TOKEN: SecretStr
    MODEL_VERSION: str = 'gpt-4-turbo'


class OllamaConfig(BaseSettings):
    OLLAMA_URL: str
    OLLAMA_MODEL: str = 'qwen2.5-coder:32b'


settings_openai = OpenAIConfig()
settings_ollama = OllamaConfig()
