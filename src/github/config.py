from pydantic import SecretStr
from pydantic_settings import BaseSettings


class GithubConfig(BaseSettings):
    GITHUB_TOKEN: SecretStr
    GITHUB_VERSION: str = '2022-11-28'
    API_URI: str = 'https://api.github.com'


settings = GithubConfig()
