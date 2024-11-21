import asyncio
import base64
import json
import mimetypes
import logging

from typing import Annotated, List
from urllib.parse import urlparse

from fastapi import HTTPException
from fastapi.params import Depends

from src.ai.client import AIClient, OllamaAdapter
from src.github.client import GithubRestAPIClient
from src.github.schemas import (
    GithubRepositoryResponse,
    GithubTreeResponse,
    GithubTreeElement,
)
from src.schemas import ReviewRequest, ReviewInAI, TextFile

logging.getLogger(__name__)


class CodeReviewAIService:
    def __init__(self, github: Annotated[GithubRestAPIClient, Depends()]):
        self.github = github
        self.ai = AIClient(ai_adapter=OllamaAdapter())
        # self.ai = AIClient(ai_adapter=OpenAIAdapter())

    async def review_repository(self, req: ReviewRequest):
        try:
            owner, repo = self.parse_uri(req.github_repo_url)
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=404, detail='Invalid GitHub repo url')
        repository = await self.get_repository(owner, repo)
        tree = await self.get_tree(owner, repo, repository.default_branch)
        # Only text files
        elements: List[GithubTreeElement] = list(
            filter(lambda e: self.is_text(e.path) and e.type != 'tree', tree.tree)
        )
        # Get content from github
        tasks = [self.get_file_content(owner, repo, e) for e in elements]
        logging.info(f'Start fetching {len(elements)} files')
        try:
            files = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        logging.info(f'Finish fetching {len(elements)} files')
        # Review content
        try:
            response = await self.ai.review_repository(
                ReviewInAI(**req.model_dump(), text_files=files)
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
        raw = response.choices[0].message.content.strip()
        raw.replace('```json\n', '').replace('```', '')
        return json.loads(raw)

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
    ) -> TextFile:
        response = await self.github.get_content(owner, repo, element.sha)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        json_data = response.json()
        return TextFile(
            path=element.path,
            content=self.decode_content(json_data['content']),
        )

    @staticmethod
    def process_data(data):
        return json.loads(data)

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
