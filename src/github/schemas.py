from typing import List

from pydantic import computed_field

from src.schemas import CodeReviewBase


class GithubRepositoryResponse(CodeReviewBase):
    id: int
    name: str
    full_name: str
    private: bool
    size: int
    language: str
    topics: List[str]
    default_branch: str


class GithubTreeElement(CodeReviewBase):
    path: str
    type: str
    sha: str
    size: None | int = None


class GithubTreeResponse(CodeReviewBase):
    url: str
    truncated: bool
    tree: List[GithubTreeElement]

    @computed_field
    @property
    def tree_length(self) -> int:
        return len(self.tree)
