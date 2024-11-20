from enum import Enum
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict

from src.constants import CandidateLevel


class CodeReviewBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        json_encoders={Enum: lambda v: v.name.lower()},
    )


class ReviewResponse(CodeReviewBase):
    found_files: int
    comments: List[str]
    rating: float
    conclusion: str


class ReviewRequest(CodeReviewBase):
    assigment_description: Annotated[str, 'Description of coding assigment']
    github_repo_url: Annotated[str, 'URL of the GitHub repository to review']
    candidate_level: Annotated[CandidateLevel, 'Junior, Middle, or Senior']
