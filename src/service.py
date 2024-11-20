import asyncio
import base64
import mimetypes

from typing import Annotated, List
from urllib.parse import urlparse

from fastapi import HTTPException
from fastapi.params import Depends

from src.github.client import GithubRestAPIClient
from src.github.schemas import (
    GithubRepositoryResponse,
    GithubTreeResponse,
    GithubTreeElement,
    GithubTextFile,
)
from src.schemas import ReviewRequest


class CodeReviewAIService:
    def __init__(self, github: Annotated[GithubRestAPIClient, Depends()]):
        self.github = github

    async def review_repository(self, req: ReviewRequest):
        try:
            owner, repo = self.parse_uri(req.github_repo_url)
        except Exception:
            raise HTTPException(status_code=404, detail='Invalid GitHub repo url')
        repository = await self.get_repository(owner, repo)
        tree = await self.get_tree(owner, repo, repository.default_branch)
        # Only text files
        elements: List[GithubTreeElement] = list(
            filter(lambda e: self.is_text(e.path) and e.type != 'tree', tree.tree)
        )
        # Get content from github
        tasks = [self.get_file_content(owner, repo, e) for e in elements]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        tree.text_files = results
        return tree

    async def get_tree(self, owner, repo, default_branch):
        response = await self.github.get_tree(owner, repo, default_branch)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return GithubTreeResponse.model_validate_json(response.content)

    async def get_repository(self, owner, repo) -> GithubRepositoryResponse:
        response = await self.github.get_repository(owner, repo)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return GithubRepositoryResponse.model_validate_json(response.content)

    async def get_file_content(
        self, owner, repo, element: GithubTreeElement
    ) -> GithubTextFile:
        response = await self.github.get_content(owner, repo, element.sha)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        json_data = response.json()
        return GithubTextFile(
            **element.model_dump(),
            content=self.decode_content(json_data['content']),
            encoding=json_data['encoding'],
        )

    @staticmethod
    def is_text(path):
        mimetype, _ = mimetypes.guess_type(path)
        return mimetype is not None and mimetype.startswith('text/')

    @staticmethod
    def decode_content(content):
        return base64.b64decode(content).decode('utf-8')

    @staticmethod
    def parse_uri(github_uri):
        uri = urlparse(github_uri)
        splited_vars = uri.path.strip().split('/')
        return splited_vars[1::]
