from enum import Enum
from typing import Annotated
from urllib.parse import urljoin

import requests
from fastapi.params import Depends
from httpx import AsyncClient

from src.github.config import settings


class GithubAPIRoutes(str, Enum):
    GET_REPOSITORY = '/repos/{owner}/{repo}'
    GET_CONTENT = '/repos/{owner}/{repo}/git/blobs/{file_sha}'
    GET_TREE = '/repos/{owner}/{repo}/git/trees/{tree_sha}'


class GithubAdapter:
    def __init__(self):
        self.api = settings.API_URI
        self.token = settings.GITHUB_TOKEN
        self.version = settings.GITHUB_VERSION
        self.client = AsyncClient()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.aclose()

    async def get(
        self, path: str, media_type: str, params: dict = None
    ) -> requests.Response:
        return await self.client.get(
            urljoin(self.api, path),
            headers={
                'Authorization': f'Bearer {self.token.get_secret_value()}',
                'Accept': media_type,
                'X-GitHub-Api-Version': self.version,
            },
            params=params,
        )


class GithubRestAPIClient:
    def __init__(self, api: Annotated[GithubAdapter, Depends()]):
        self.api = api

    async def get_repository(self, owner, repo) -> requests.Response:
        req_uri = GithubAPIRoutes.GET_REPOSITORY.format(owner=owner, repo=repo)
        response = await self.api.get(req_uri, media_type='application/vnd.github+json')
        return response

    async def get_content(self, owner, repo, file_sha) -> requests.Response:
        req_uri = GithubAPIRoutes.GET_CONTENT.format(
            owner=owner, repo=repo, file_sha=file_sha
        )
        response = await self.api.get(req_uri, media_type='application/vnd.github+json')
        return response

    async def get_tree(self, owner, repo, tree_sha) -> requests.Response:
        req_uri = GithubAPIRoutes.GET_TREE.format(
            owner=owner, repo=repo, tree_sha=tree_sha
        )
        response = await self.api.get(
            req_uri,
            media_type='application/vnd.github+json',
            params={'recursive': 'true'},
        )
        return response
